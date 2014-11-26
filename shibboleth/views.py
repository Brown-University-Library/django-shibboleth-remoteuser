

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from urllib import quote

#Logout settings.
from shibboleth.app_settings import SHIBBOLETH_LOGIN_URL, SHIBBOLETH_LOGOUT_URL, LOGOUT_REDIRECT_URL

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

class ShibbolethLoginView(TemplateView):
    """
    Pass the user to the Shibboleth logout page.
    Some code borrowed from:
    https://github.com/stefanfoulis/django-class-based-auth-views.
    """
    redirect_field_name = "next"

    def get(self, *args, **kwargs):
        #Remove session value that is forcing Shibboleth reauthentication.
        self.request.session.pop(LOGOUT_SESSION_KEY, None)
        login = SHIBBOLETH_LOGIN_URL + '?target=%s' % quote(self.request.GET.get(self.redirect_field_name))
        return redirect(login)
    
class ShibbolethLogoutView(TemplateView):
    """
    Pass the user to the Shibboleth logout page.
    Some code borrowed from:
    https://github.com/stefanfoulis/django-class-based-auth-views.
    """
    redirect_field_name = "next"

    def get(self, *args, **kwargs):
        #Log the user out. This means a full logout from shibboleth. There is no such thing as logging out from the service, but staying logged into shibboleth. It is single-sign on. Either you're signed in to all, or not.
        auth.logout(self.request)
        target = LOGOUT_REDIRECT_URL or\
                 quote(self.request.GET.get(self.redirect_field_name)) or\
                 quote(request.build_absolute_uri())
        logout = SHIBBOLETH_LOGOUT_URL + '?target=%s' % target

        return redirect(logout)


