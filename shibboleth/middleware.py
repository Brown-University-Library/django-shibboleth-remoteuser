from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured

from shibboleth.app_settings import LOGOUT_SESSION_KEY

class ShibbolethRemoteUserMiddleware(RemoteUserMiddleware):
    """
    Authentication Middleware for use with Shibboleth.  Uses the recommended pattern
    for remote authentication from: http://code.djangoproject.com/svn/django/tags/releases/1.3/django/contrib/auth/middleware.py
    """
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        #To support logout.  If this variable is True, do not
        #authenticate user and return now.
        if request.session.get(LOGOUT_SESSION_KEY) == True:
            return
        else:
            #Delete the shib reauth session key if present.
	        request.session.pop(LOGOUT_SESSION_KEY, None)

        #Locate the remote user header.
        try:
            # self.header is set to REMOTE_USER. This is what the user CLAIMS to be.
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then return (leaving
            # request.user set to AnonymousUser by the
            # AuthenticationMiddleware).
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.username == self.clean_username(username, request):
                return


        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        # The last two arguments look strang and in fact I want to remove them as I think they reflect a security problem.
        user = auth.authenticate(remote_user=username, META_HEADERS=request.META, session=request.session)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
            user.set_unusable_password()
            user.save()
            # call make profile.
            #self.make_profile(user, shib_meta)
            #setup session.
            #self.setup_session(request)

    # def make_profile(self, user, shib_meta):
    #     """
    #     This is here as a stub to allow subclassing of ShibbolethRemoteUserMiddleware
    #     to include a make_profile method that will create a Django user profile
    #     from the Shib provided attributes.  By default it does nothing.
    #     """
    #     return

    # def setup_session(self, request):
    #     """
    #     If you want to add custom code to setup user sessions, you
    #     can extend this.
    #     """
    #     return

