from django.conf.urls.defaults import *

from views import ShibbolethView, ShibbolethLogoutView

urlpatterns = patterns('', 
    url(r'^logout/$', ShibbolethLogoutView.as_view()),
    url(r'^$', ShibbolethView.as_view()),
)