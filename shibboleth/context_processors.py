try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from urllib.parse import quote

try:
    from app_settings import LOGOUT_URL, LOGOUT_REDIRECT_URL, LOGIN_REDIRECT_URL, LOGIN_URL_PARAMETER
except ImportError:
    from .app_settings import LOGOUT_URL, LOGOUT_REDIRECT_URL, LOGIN_REDIRECT_URL, LOGIN_URL_PARAMETER

def login_link(request):
    """
    By default: this assumes your login link is the Shibboleth login page for your server
    and uses the 'target' url parameter.
    """
    full_path = LOGIN_REDIRECT_URL or quote(request.get_full_path())
    login = reverse('shibboleth:login')
    ll = "%s?%s=%s" % (login, LOGIN_URL_PARAMETER, full_path)
    return { 'login_link': ll }

def logout_link(request, *args):
    """
    This assumes your login link is the Shibboleth login page for your server
    and uses the 'target' url parameter.
    e.g: https://school.edu/Shibboleth.sso/Login
    """
    #LOGOUT_REDIRECT_URL specifies a default logout page that will always be used when
    #users logout from Shibboleth.
    target = LOGOUT_REDIRECT_URL or quote(request.build_absolute_uri())
    logout = reverse('shibboleth:logout')
    ll = "%s?target=%s" % (logout, target)
    return { 'logout_link': ll }
