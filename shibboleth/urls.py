import django
from django.conf.urls import url
from shibboleth.app_settings import SINGLE_LOGOUT_BACKCHANNEL

from .views import ShibbolethView, ShibbolethLogoutView, ShibbolethLoginView

urlpatterns = [
    url(r'^login/$', ShibbolethLoginView.as_view(), name='login'),
    url(r'^logout/$', ShibbolethLogoutView.as_view(), name='logout'),
    url(r'^$', ShibbolethView.as_view(), name='info'),
]

if SINGLE_LOGOUT_BACKCHANNEL:
    from spyne.protocol.soap import Soap11
    from spyne.server.django import DjangoView
    from .slo_view import LogoutNotificationService

    urlpatterns += [
        url(r'^logoutNotification/', DjangoView.as_view(
            services=[LogoutNotificationService],
            tns='urn:mace:shibboleth:2.0:sp:notify',
            in_protocol=Soap11(validator='lxml'), out_protocol=Soap11())),
    ]
