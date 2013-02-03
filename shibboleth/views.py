

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

#Logout settings.
from shibboleth.app_settings import LOGOUT_URL, LOGOUT_REDIRECT_URL, LOGOUT_SESSION_KEY

class ShibbolethView(TemplateView):
    """
    This is here to offer a Shib protected page that we can
    route users through to login.
    """
    template_name = 'shibboleth/user_info.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Django docs say to decorate the dispatch method for 
        class based views.
        https://docs.djangoproject.com/en/dev/topics/auth/
        """
        return super(ShibbolethView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, **kwargs):
        """Process the request."""
        next = self.request.GET.get('next', None)
        if next is not None:
            return redirect(next)
        return super(ShibbolethView, self).get(request)
    
    def get_context_data(self, **kwargs):
        context = super(ShibbolethView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class ShibbolethLogoutView(TemplateView):
    """
    Pass the user to the Shibboleth logout page.
    Some code borrowed from:
    https://github.com/stefanfoulis/django-class-based-auth-views.
    """
    redirect_field_name = "target"

    def get(self, *args, **kwargs):
        next = self.get_redirect_url()
        if not self.request.user.is_authenticated():
            return redirect(next)
        #Log the user out.
        auth.logout(self.request)
        #Set session key that middleware will use to force 
        #Shibboleth reauthentication.
        self.request.session[LOGOUT_SESSION_KEY] = True
        return redirect(self.get_shib_logout_path())

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        #Log the user out.
        auth.logout(self.request)
        #Set session key that middleware will use to force 
        #Shibboleth reauthentication.
        self.request.session[LOGOUT_SESSION_KEY] = True
        return redirect(self.get_shib_logout_path())

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def get_redirect_url(self, next_url=None, **kwargs):
        """
        URL to send user after logout.
        """
        if next_url is None:
            next_url = LOGOUT_REDIRECT_URL
            if next_url is None:
                next_url = self.request.META.get('HTTP_REFERRER')
        if next_url is None:
            raise ImproperlyConfigured("Target url not found.")
        return next_url

    def get_shib_logout_path(self):
        next = self.get_redirect_url()
        logout_path = LOGOUT_URL % next
        return logout_path