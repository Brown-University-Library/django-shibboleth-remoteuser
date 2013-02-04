
def login_link(request):
    """
    This assumes your login link is the Shibboleth login page for your server 
    and uses the 'target' url parameter.
    e.g: https://school.edu/Shibboleth.sso/Login
    """
    from app_settings import LOGIN_URL
    from urllib import quote
    full_path = quote(request.get_full_path())
    ll = "%s?target=%s" % (LOGIN_URL, full_path)
    return { 'login_link': ll }

def logout_link(request, *args):
    """
    This assumes your login link is the Shibboleth login page for your server 
    and uses the 'target' url parameter.
    e.g: https://school.edu/Shibboleth.sso/Login
    """
    from app_settings import LOGOUT_URL, LOGOUT_REDIRECT_URL
    from urllib import quote
    #Use the app setting logout redirect url if present
    #else bring the user back to the current page.
    if LOGOUT_REDIRECT_URL:
        next_path = LOGOUT_REDIRECT_URL
    else:
        next_path = request.get_full_path()
    ll = "%s?target=%s" % (LOGOUT_URL, quote(next_path))
    return { 'logout_link': ll }