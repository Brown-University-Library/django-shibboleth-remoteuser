import django
from django.urls import re_path

from .views import ShibbolethView, ShibbolethLogoutView, ShibbolethLoginView

app_name = 'shibboleth'

urlpatterns = [
    re_path(r'^login/$', ShibbolethLoginView.as_view(), name='login'),
    re_path(r'^logout/$', ShibbolethLogoutView.as_view(), name='logout'),
    re_path(r'^$', ShibbolethView.as_view(), name='info'),
]
