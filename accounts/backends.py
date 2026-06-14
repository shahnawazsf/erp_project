import logging

import oracledb
from django.contrib.auth.backends import BaseBackend
from django.db import connection

from .models import User

logger = logging.getLogger(__name__)

_VALID_ROLES = frozenset(role for role, _ in User.ROLE_CHOICES)


def _call_get_user_detail(username, password):
    """
    Call Oracle stored procedure GET_USER_DETAIL.

    Actual signature (verified via user_arguments):
        GET_USER_DETAIL(
            P_USER_ID       IN  VARCHAR2,   -- username / login ID
            P_PASSWORD      IN  VARCHAR2,
            P_USER_NAME     OUT VARCHAR2,   -- full name
            P_USER_GRP_ID   OUT VARCHAR2,   -- group / role
            P_USER_EMP_CODE OUT VARCHAR2,   -- employee code
            P_USER_DESC     OUT VARCHAR2,   -- description
            P_STATUS        OUT VARCHAR2    -- 'SUCCESS' or other
        )

    Returns a user-info dict on SUCCESS, None on failure.
    """
    with connection.cursor() as django_cur:
        # django_cur.cursor  → Django's FormatStylePlaceholderCursor
        # .cursor on that    → raw oracledb cursor (needed so .var() returns
        #                      oracledb.Var, not Django's VariableWrapper)
        cur = django_cur.cursor.cursor

        p_user_name     = cur.var(oracledb.STRING)
        p_user_grp_id   = cur.var(oracledb.STRING)
        p_user_emp_code = cur.var(oracledb.STRING)
        p_user_desc     = cur.var(oracledb.STRING)
        p_status        = cur.var(oracledb.STRING)

        cur.callproc('SDESERP.GET_USER_DETAIL', [
            username, password,
            p_user_name, p_user_grp_id, p_user_emp_code,
            p_user_desc, p_status,
        ])

        status = p_status.getvalue()
        if status != 'TRUE':
            logger.warning(
                'GET_USER_DETAIL returned status=%r for username=%r',
                status, username,
            )
            return None

        # Map P_USER_GRP_ID to a valid Django role; fall back to 'employee'
        raw_role = (p_user_grp_id.getvalue() or '').lower()
        if raw_role not in _VALID_ROLES:
            logger.warning(
                'GET_USER_DETAIL returned unknown group %r for username=%r; '
                'defaulting to "employee"',
                raw_role, username,
            )
            raw_role = 'employee'

        # Split full name into first / last (best-effort)
        full_name  = (p_user_name.getvalue() or '').strip()
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name  = name_parts[1] if len(name_parts) > 1 else ''

        return {
            'first_name': first_name,
            'last_name':  last_name,
            'role':       raw_role,
            'emp_code':   p_user_emp_code.getvalue() or '',
            'desc':       p_user_desc.getvalue() or '',
        }


class OracleProcedureBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            info = _call_get_user_detail(username, password)
        except Exception:
            logger.exception(
                'Unexpected error calling GET_USER_DETAIL for username=%r', username,
            )
            return None

        if info is None:
            return None

        is_admin = (info['role'] == 'admin')

        user, created = User.objects.get_or_create(username=username)
        user.first_name   = info['first_name']
        user.last_name    = info['last_name']
        user.role         = info['role']
        user.is_active    = True
        user.is_staff     = is_admin   # grants Django admin panel access
        user.is_superuser = is_admin   # refreshed on every login
        user.set_unusable_password()   # password lives in Oracle, not Django
        user.save()

        if created:
            logger.info('Auto-created Django user row for %r', username)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
