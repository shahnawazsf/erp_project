from .oracle_auth import OracleUser, SESSION_KEY


class OracleAuthMiddleware:
    """
    Reads oracle_user from the session and sets request.user to an OracleUser
    instance, overriding Django's AuthenticationMiddleware result.
    Must be placed AFTER AuthenticationMiddleware in settings.MIDDLEWARE.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        data = request.session.get(SESSION_KEY)
        if data:
            request.user = OracleUser(data)
        return self.get_response(request)
