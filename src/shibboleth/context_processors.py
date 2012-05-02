

def login_link(request):
    from app_settings import LOGIN_URL
    ll = "%s?next=%s" % (LOGIN_URL, request.get_full_path())
    return { 'login_link': ll }