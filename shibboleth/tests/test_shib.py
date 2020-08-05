# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.utils import IntegrityError
from django.test import TestCase, RequestFactory
from django import VERSION

User = get_user_model()

SAMPLE_HEADERS = {
  "REMOTE_USER": 'sampledeveloper@school.edu',
  "Shib-Application-ID": "default", 
  "Shib-Authentication-Method": "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified", 
  "Shib-AuthnContext-Class": "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified", 
  "Shib-Identity-Provider": "https://sso.college.edu/idp/shibboleth", 
  "Shib-Session-ID": "1", 
  "Shib-Session-Index": "12", 
  "Shibboleth-affiliation": "member@college.edu;staff@college.edu", 
  "Shibboleth-schoolBarCode": "12345678",
  "Shibboleth-schoolNetId": "Sample_Developer", 
  "Shibboleth-schoolStatus": "active", 
  "Shibboleth-department": "University Library, Integrated Technology Services", 
  "Shibboleth-displayName": "Sample Developer", 
  "Shibboleth-eppn": "sampledeveloper@school.edu", 
  "Shibboleth-givenName": "Sample", 
  "Shibboleth-isMemberOf": "SCHOOL:COMMUNITY:EMPLOYEE:ADMINISTRATIVE:BASE;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:P;COMMUNITY:ALL;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:M;", 
  "Shibboleth-isMemberOf-multi-delimiter": "SCHOOL:COMMUNITY:EMPLOYEE:ADMINISTRATIVE:BASE,SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:P,COMMUNITY:ALL;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:M,",
  "Shibboleth-mail": "Sample_Developer@school.edu", 
  "Shibboleth-persistent-id": "https://sso.college.edu/idp/shibboleth!https://server.college.edu/shibboleth-sp!sk1Z9qKruvXY7JXvsq4GRb8GCUk=", 
  "Shibboleth-sn": "Developer", 
  "Shibboleth-title": "Library Developer", 
  "Shibboleth-unscoped-affiliation": "member;staff",
}

settings.SHIBBOLETH_ATTRIBUTE_MAP = {
   "Shib-Identity-Provider": (True, "idp"),
   "Shibboleth-mail": (True, "email"),
   "Shibboleth-eppn": (True, "username"),
   "Shibboleth-schoolStatus": (True, "status"),
   "Shibboleth-affiliation": (True, "affiliation"),
   "Shib-Session-ID": (True, "session_id"),
   "Shibboleth-givenName": (True, "first_name"),
   "Shibboleth-sn": (True, "last_name"),
   "Shibboleth-schoolBarCode": (False, "barcode"),
   "Shibboleth-displayName": (True, "shortened_name", lambda x: x[:5])
}


settings.AUTHENTICATION_BACKENDS += (
    'shibboleth.backends.ShibbolethRemoteUserBackend',
)

if VERSION[0] < 2 and VERSION[1] < 10:
    settings.MIDDLEWARE_CLASSES = tuple(settings.MIDDLEWARE) + (
        'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    )
else:
    settings.MIDDLEWARE += [
        'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    ]

settings.ROOT_URLCONF = 'shibboleth.urls'

settings.SHIBBOLETH_LOGOUT_URL = 'https://sso.school.edu/logout?next=%s'
settings.SHIBBOLETH_LOGOUT_REDIRECT_URL = 'http://school.edu/'

# MUST be imported after the settings above
from shibboleth import app_settings
from shibboleth import middleware
from shibboleth import backends


try:
    from importlib import reload  # python 3.4+
except ImportError:
    try:
        from imp import reload # for python 3.2/3.3
    except ImportError:
        pass # this means we're on python 2, where reload is a builtin function


class AttributesTest(TestCase):
        
    def test_decorator_not_authenticated(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        # Test the context - shouldn't exist
        self.assertEqual(resp.context, None) 
        
    def test_decorator_authenticated(self):
        resp = self.client.get('/', **SAMPLE_HEADERS)
        self.assertEqual(resp.status_code, 200)
        # Test the context
        user = resp.context.get('user')
        self.assertEqual(user.email, 'Sample_Developer@school.edu')
        self.assertEqual(user.first_name, 'Sample')
        self.assertEqual(user.last_name, 'Developer')
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_anonymous)


class TestShibbolethRemoteUserMiddleware(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.smw = SessionMiddleware()
        self.amw = AuthenticationMiddleware()
        self.rmw = RemoteUserMiddleware()
        self.srmw = middleware.ShibbolethRemoteUserMiddleware()

    def _process_request_through_middleware(self, request):
        self.smw.process_request(request)
        self.amw.process_request(request)
        self.rmw.process_request(request)
        return self.srmw.process_request(request)

    def test_no_remote_user(self):
        test_request = self.request_factory.get('/')
        self._process_request_through_middleware(test_request)
        #shouldn't have done anything - just return because no REMOTE_USER
        self.assertTrue('shib' not in test_request.session)
        self.assertFalse(test_request.user.is_authenticated)

    def test_remote_user_empty(self):
        test_request = self.request_factory.get('/', REMOTE_USER='')
        response = self._process_request_through_middleware(test_request)
        self.assertTrue('shib' not in test_request.session)
        self.assertFalse(test_request.user.is_authenticated)


class TestShibbolethRemoteUserBackend(TestCase):

    def _get_valid_shib_meta(self, location='/'):
        request_factory = RequestFactory()
        test_request = request_factory.get(location)
        test_request.META.update(**SAMPLE_HEADERS)
        shib_meta, error = middleware.ShibbolethRemoteUserMiddleware.parse_attributes(test_request)
        self.assertFalse(error, 'Generating shibboleth attribute mapping contains errors')
        return shib_meta

    def test_create_unknown_user_true(self):
        self.assertFalse(User.objects.all())
        shib_meta = self._get_valid_shib_meta()
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertEqual(user.username, 'sampledeveloper@school.edu')
        self.assertEqual(User.objects.all()[0].username, 'sampledeveloper@school.edu')

    def test_create_unknown_user_false(self):
        with self.settings(CREATE_UNKNOWN_USER=False):
            # reload our shibboleth.backends module, so it picks up the settings change
            reload(backends)
            shib_meta = self._get_valid_shib_meta()
            self.assertFalse(User.objects.all())
            user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
            self.assertTrue(user is None)
            self.assertFalse(User.objects.all())
        # now reload again, so it reverts to original settings
        reload(backends)

    def test_auth_inactive_user_false(self):
        shib_meta = self._get_valid_shib_meta()
        # Pre-create an inactive user
        User.objects.create(username='sampledeveloper@school.edu', is_active=False)
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertTrue(user is None)

    def test_ensure_user_attributes(self):
        shib_meta = self._get_valid_shib_meta()
        # Create / authenticate the test user and store another mail address
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        user.email = 'invalid_email@school.edu'
        user.save()
        # The user must contain the invalid mail address
        user = User.objects.get(username='sampledeveloper@school.edu')
        self.assertEqual(user.email, 'invalid_email@school.edu')
        # After authenticate the user again, the mail address must be set back to the shibboleth data
        user2 = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertEqual(user2.email, 'Sample_Developer@school.edu')

    def test_authenticate_with_exclude_field(self):
        shib_meta = self._get_valid_shib_meta()
        shib_meta['email'] = None
        # email is a required field at the ORM level, passing None throws an error
        with self.assertRaises(IntegrityError):
            auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)

        # using the exclude absent option works correctly
        shib_meta.pop('email')
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertEqual(user.email, '')


class TestShibbolethParseAttributes(TestCase):

    def setUp(self):
        request_factory = RequestFactory()
        self.test_request = request_factory.get('/')
        self.test_request.META.update(**SAMPLE_HEADERS)

    def test_present_required_attribute(self):
        shib_meta, error = middleware.ShibbolethRemoteUserMiddleware.parse_attributes(self.test_request)
        self.assertEqual(shib_meta["last_name"], SAMPLE_HEADERS["Shibboleth-sn"])
        self.assertFalse(error)

    def test_missing_required_attribute(self):
        self.test_request.META.pop("Shibboleth-sn")
        shib_meta, error = middleware.ShibbolethRemoteUserMiddleware.parse_attributes(self.test_request)
        self.assertTrue(error)

    def test_present_optional_attribute(self):
        shib_meta, error = middleware.ShibbolethRemoteUserMiddleware.parse_attributes(self.test_request)
        self.assertEqual(shib_meta["barcode"], SAMPLE_HEADERS["Shibboleth-schoolBarCode"])
        self.assertFalse(error)

    def test_missing_optional_attribute(self):
        self.test_request.META.pop("Shibboleth-schoolBarCode")
        shib_meta, error = middleware.ShibbolethRemoteUserMiddleware.parse_attributes(self.test_request)
        self.assertFalse('barcode' in shib_meta.keys())
        self.assertFalse(error)

    def test_mutated_attribute(self):
        shib_meta, error = middleware.ShibbolethRemoteUserMiddleware.parse_attributes(self.test_request)
        self.assertEqual(shib_meta["barcode"], SAMPLE_HEADERS["Shibboleth-schoolBarCode"])
        self.assertEqual(shib_meta["shortened_name"], SAMPLE_HEADERS["Shibboleth-displayName"][:5])

class TestShibbolethGroupAssignment(TestCase):

    def test_unconfigured_group(self):
        # by default SHIBBOLETH_GROUP_ATTRIBUTES = [] - so no groups will be touched
        with self.settings(SHIBBOLETH_GROUP_ATTRIBUTES=[]):
            reload(app_settings)
            reload(middleware)
            # After login the user will be created
            self.client.get('/', **SAMPLE_HEADERS)
            query = User.objects.filter(username='sampledeveloper@school.edu')
            # Ensure the user was created
            self.assertEqual(len(query), 1)
            user = User.objects.get(username='sampledeveloper@school.edu')
            # The user should have no groups
            self.assertEqual(len(user.groups.all()), 0)
            # Create a group and add the user
            g = Group(name='Testgroup')
            g.save()
            # Now we should have exactly one group
            self.assertEqual(len(Group.objects.all()), 1)
            g.user_set.add(user)
            # Now the user should be in exactly one group
            self.assertEqual(len(user.groups.all()), 1)
            self.client.get('/', **SAMPLE_HEADERS)
            # After a request the user should still be in the group.
            self.assertEqual(len(user.groups.all()), 1)

    def test_group_creation(self):
        # Test for group creation
        with self.settings(SHIBBOLETH_GROUP_ATTRIBUTES=['Shibboleth-affiliation']):
            reload(app_settings)
            reload(middleware)
            self.client.get('/', **SAMPLE_HEADERS)
            user = User.objects.get(username='sampledeveloper@school.edu')
            self.assertEqual(len(Group.objects.all()), 2)
            self.assertEqual(len(user.groups.all()), 2)

    def test_group_creation_list(self):
        # Test for group creation from a list of group attributes
        with self.settings(SHIBBOLETH_GROUP_ATTRIBUTES=['Shibboleth-affiliation', 'Shibboleth-isMemberOf']):
            reload(app_settings)
            reload(middleware)
            self.client.get('/', **SAMPLE_HEADERS)
            user = User.objects.get(username='sampledeveloper@school.edu')
            self.assertEqual(len(Group.objects.all()), 6)
            self.assertEqual(len(user.groups.all()), 6)

    def test_group_creation_list_comma(self):
        # Test for group creation from a list of group attributes with a different delimiter
        with self.settings(SHIBBOLETH_GROUP_ATTRIBUTES=['Shibboleth-isMemberOf-multi-delimiter'],
                           SHIBBOLETH_GROUP_DELIMITERS=[',']):
            reload(app_settings)
            reload(middleware)
            self.client.get('/', **SAMPLE_HEADERS)
            user = User.objects.get(username='sampledeveloper@school.edu')
            self.assertEqual(len(Group.objects.all()), 3)
            self.assertEqual(len(user.groups.all()), 3)

    def test_group_creation_list_mixed_comma_semicolon(self):
        # Test for group creation from a list of group attributes with multiple delimiters
        with self.settings(SHIBBOLETH_GROUP_ATTRIBUTES=['Shibboleth-affiliation', 'Shibboleth-isMemberOf-multi-delimiter'],
                           SHIBBOLETH_GROUP_DELIMITERS=[',', ';']):
            reload(app_settings)
            reload(middleware)
            self.client.get('/', **SAMPLE_HEADERS)
            user = User.objects.get(username='sampledeveloper@school.edu')
            self.assertEqual(len(Group.objects.all()), 6)
            self.assertEqual(len(user.groups.all()), 6)

    def test_empty_group_attribute(self):
        # Test everthing is working even if the group attribute is missing in the shibboleth data
        with self.settings(SHIBBOLETH_GROUP_ATTRIBUTES=['Shibboleth-not-existing-attribute']):
            reload(app_settings)
            reload(middleware)
            self.client.get('/', **SAMPLE_HEADERS)
            user = User.objects.get(username='sampledeveloper@school.edu')
            self.assertEqual(len(Group.objects.all()), 0)
            self.assertEqual(len(user.groups.all()), 0)


class LogoutTest(TestCase):

    def test_logout(self):
        # Login
        login = self.client.get('/', **SAMPLE_HEADERS)
        self.assertEqual(login.status_code, 200)
        # Check login
        login = self.client.get('/')
        self.assertEqual(login.status_code, 200)
        # Logout
        logout = self.client.get('/logout/', **SAMPLE_HEADERS)
        self.assertEqual(logout.status_code, 302)
        # Ensure redirect happened.
        self.assertEqual(
            logout['Location'],
            'https://sso.school.edu/logout?next=http://school.edu/'
        )
        # Load root url to see if user is in fact logged out.
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        # Make sure the context is empty.
        self.assertEqual(resp.context, None)
