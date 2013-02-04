from django.conf.urls.defaults import *

from views import ShibbolethView, ShibbolethLogoutView

urlpatterns = patterns('', 
    url(r'^logout/$', ShibbolethLogoutView.as_view(), name='shibboleth-logout'),
    url(r'^$', ShibbolethView.as_view(), name='shibboleth'),
)