from django.contrib.sessions.models import Session
from shibboleth.models import ShibSession
#SLO (back-channel) / spyne stuff
from spyne.model.primitive import Unicode
#from spyne.model import XmlAttribute
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


class LogoutNotificationService(Service):
    @rpc(MandatoryUnicode, _returns=OKType,
         _in_variable_names={'sessionid': 'SessionID'},
         _out_variable_name='OK',
         )
    def LogoutNotification(ctx, sessionid):
        # delete user session based on shib session
        try:
            session_mapping = ShibSession.objects.get(shib=sessionid)
        except:
            # Can't delete session
            raise Fault(faultcode='Client', faultstring='Invalid session id')
        else:
            # Deleting session
            Session.objects.filter(session_key=session_mapping.session_id).delete()
            return True
