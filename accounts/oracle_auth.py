import logging

import oracledb
from django.db import connection

logger = logging.getLogger(__name__)

SESSION_KEY = 'oracle_user'


def call_get_user_detail(username, password):
    """
    Call GET_USER_DETAIL(P_USER_ID IN, P_PASSWORD IN,
                         P_USER_NAME OUT, P_USER_GRP_ID OUT,
                         P_USER_EMP_CODE OUT, P_USER_DESC OUT,
                         P_STATUS OUT).
    Returns a dict on success ('TRUE'), None on failure.
    Also queries LOGIN_USER table for USER_ROLE.
    """
    with connection.cursor() as django_cur:
        cur = django_cur.cursor.cursor          # raw oracledb cursor

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
            logger.warning('GET_USER_DETAIL: status=%r for username=%r', status, username)
            return None

        # Map Oracle roles to permission system roles
        role_mapping = {
            'A': 'admin',      # Admin
            'U': 'employee',   # User
        }
        oracle_role = (p_user_grp_id.getvalue() or '').strip().upper()
        user_role = role_mapping.get(oracle_role, 'employee')

        user_data = {
            'username':      username,
            'user_name':     p_user_name.getvalue() or '',
            'user_grp_id':   p_user_grp_id.getvalue() or '',
            'user_emp_code': p_user_emp_code.getvalue() or '',
            'user_desc':     p_user_desc.getvalue() or '',
            'role':          user_role,
        }
        logger.debug('Mapped user role %r → %r for %s', oracle_role, user_role, username)

        return user_data


class OracleUser:
    """
    Lightweight user object built from Oracle session data.
    Not a Django model — never touches the database.
    Satisfies request.user.is_authenticated so @login_required works.
    """
    is_anonymous = False
    is_authenticated = True

    def __init__(self, data):
        self.username      = data['username']
        self.user_name     = data.get('user_name', '')
        self.user_grp_id   = data.get('user_grp_id', '')
        self.user_emp_code = data.get('user_emp_code', '')
        self.user_desc     = data.get('user_desc', '')
        self.role          = data.get('role', 'employee')

    def get_full_name(self):
        return self.user_name

    def has_role(self, *roles):
        return self.role in roles

    def __str__(self):
        return self.username
