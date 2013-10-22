"""
For tests only.  Sample ShibbolethRemoteUserMiddleware class.
"""

from shibboleth.middleware import ShibbolethRemoteUserMiddleware

class ShibTestMiddleware(ShibbolethRemoteUserMiddleware):
    #def process_request(self, request):
    #    super(ShibbolethRemoteUserMiddleware, self).process_request(request)

    def after_login(self, request, user):
        """
        Create a user after login.
        """
        ShibbolethRemoteUserMiddleware.create_user(self, request, user)