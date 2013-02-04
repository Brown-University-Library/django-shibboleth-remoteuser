from django.core.urlresolvers import reverse
from urllib import quote

def login_link(request):
    """
    This assumes your login link is the Shibboleth login page for your server 
    and uses the 'target' url parameter.
    e.g: https://school.edu/Shibboleth.sso/Login
    """
    from app_settings import LOGIN_URL
    full_path = quote(request.get_full_path())
    login = reverse('shibboleth:login')
    ll = "%s?target=%s" % (login, full_path)
    return { 'login_link': ll }

def logout_link(request, *args):
    """
    This assumes your login link is the Shibboleth login page for your server 
    and uses the 'target' url parameter.
    e.g: https://school.edu/Shibboleth.sso/Login
    """
    from app_settings import LOGOUT_URL, LOGOUT_REDIRECT_URL
    out = reverse('shibboleth:logout')
    ll = "%s?target=%s" % (out, quote(LOGOUT_REDIRECT_URL))
    return { 'logout_link': ll }