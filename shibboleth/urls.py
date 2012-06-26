from django.conf.urls.defaults import *

from views import ShibbolethView

urlpatterns = patterns('', 
    url(r'^$', ShibbolethView.as_view()),
)