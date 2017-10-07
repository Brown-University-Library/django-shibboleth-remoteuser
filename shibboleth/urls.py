import django
from django.conf.urls import url
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoView

from .views import ShibbolethView, ShibbolethLogoutView, ShibbolethLoginView, LogoutNotificationService

urlpatterns = [
    url(r'^login/$', ShibbolethLoginView.as_view(), name='login'),
    url(r'^logout/$', ShibbolethLogoutView.as_view(), name='logout'),
    url(r'^$', ShibbolethView.as_view(), name='info'),
    url(r'^logoutNotification/', DjangoView.as_view(
        services=[LogoutNotificationService], tns='urn:mace:shibboleth:2.0:sp:notify',
        in_protocol=Soap11(), out_protocol=Soap11())),
        #cache_wsdl=False)),
        #FIXME Soap11(validator='lxml') - validation would be nice, but needs adjusted model to support logout type attribute
]
