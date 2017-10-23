from django.contrib.sessions.models import Session
from shibboleth.models import ShibSession
#SLO (back-channel) / spyne stuff
from spyne.model.primitive import Unicode
from spyne.model import XmlAttribute
from spyne.model.enum import Enum
try:
    from spyne.service import Service
except ImportError:
    from spyne.service import ServiceBase as Service

from spyne.decorator import rpc
from spyne import ComplexModel
from spyne.model.fault import Fault


class OKType(ComplexModel):
    pass


class MandatoryUnicode(Unicode):
    class Attributes(Unicode.Attributes):
        nullable = False
        min_occurs = 1


class LogoutRequest(ComplexModel):
    __namespace__ = 'urn:mace:shibboleth:2.0:sp:notify'
    SessionID = MandatoryUnicode
    type = XmlAttribute(Enum("global", "local",
                        type_name="LogoutNotificationType"))


class LogoutResponse(ComplexModel):
    __namespace__ = 'urn:mace:shibboleth:2.0:sp:notify'
    OK = OKType


class LogoutNotificationService(Service):
    @rpc(LogoutRequest, _returns=LogoutResponse, _body_style='bare')
    def LogoutNotification(ctx, req):
        # delete user session based on shib session
        try:
            session_mapping = ShibSession.objects.get(shib=req.SessionID)
        except:
            # Can't delete session
            raise Fault(faultcode='Client', faultstring='Invalid session id')
        else:
            # Deleting session
            Session.objects.filter(
                session_key=session_mapping.session_id).delete()
            return LogoutResponse
