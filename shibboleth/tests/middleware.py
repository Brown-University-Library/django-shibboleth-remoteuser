"""
For tests only.  Sample ShibbolethRemoteUserMiddleware class.
"""

from shibboleth.middleware import ShibbolethRemoteUserMiddleware

class ShibTestMiddleware(ShibbolethRemoteUserMiddleware):

    def after_login(self, request, user):
        """
        Assign user attributes from Shibboleth after login.
        """
        ShibbolethRemoteUserMiddleware.create_user(self, request, user)