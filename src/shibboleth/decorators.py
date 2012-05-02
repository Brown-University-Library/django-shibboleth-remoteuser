
from shibboleth.middleware import parse_attributes

def login_optional(func):
  """
  Decorator to pull Shib attributes and log user in possible.  Does not 
  enforce login.
  """
  def decorator(request,*args, **kwargs):
    #Do nothing if the remoteuser backend isn't activated
    if 'django.contrib.auth.backends.RemoteUserBackend' not in settings.AUTHENTICATION_BACKENDS:
        pass
    else:
        shib, error = parse_attributes(request)
        if error == False:
            #log the user in
            username = shib.get('username')
            user = auth.authenticate(remote_user=username)
            auth.login(request, user)
            user.set_unusable_password()
            user.first_name = shib.get('first_name', None)
            user.last_name = shib.get('last_name', None)
            user.email = shib.get('email', None)
            user.save()
    return func(request, *args, **kwargs)
  return decorator 