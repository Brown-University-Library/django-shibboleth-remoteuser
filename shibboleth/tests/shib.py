# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import unittest
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.client import Client

import os
from pprint import pprint

from shibboleth.views import ShibbolethView

SAMPLE_HEADERS = {
  "REMOTE_USER": 'devloper@school.edu',
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
  "Shibboleth-isMemberOf": "SCHOOL:COMMUNITY:EMPLOYEE:ADMINISTRATIVE:BASE;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:P;COMMUNITY:ALL;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:M;SCHOOL:SERVICES:RIGHTANSWERS:USERS;SCHOOL:COMMUNITY:PRESIDENT:ALL;SCHOOL:COMMUNITY:LICENSE:FACSTAFF;SCHOOL:COMMUNITY:ALL;SCHOOL:COMMUNITY:LICENSE:FACSTAFFMS;SCHOOL:COMMUNITY:ADMIN:MM:PROD:COMMUNITY:EMPLOYEE:EXEMPT:ALL;SCHOOL:COMMUNITY:PRESIDENT:ON_OFF_CAMPUS;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:EXEMPT_NONEXEMPT;SCHOOL:COMMUNITY:EMPLOYEE:BENEFITS:NOUNION;SCHOOL:COMMUNITY:EMPLOYEE:ALL;SCHOOL:COMMUNITY:TRANSPORTATION:FACSTAFF;SCHOOL:COMMUNITY:EMPLOYEE:NONSTUDENT;SCHOOL:COMMUNITY:LICENSE:FACSTAFFGRAD;SCHOOL:COMMUNITY:LICENSE:FACSTAFFNONMED;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:EXEMPT_NONEXEMPT_UNION;SCHOOL:SERVICES:LIBRARY:ERESOURCES;SCHOOL:COMMUNITY:EMPLOYEE:ADMINISTRATIVE:ALL;SCHOOL:COMMUNITY:LICENSE:ALL;SCHOOL:COMMUNITY:EMPLOYEE:ONCAMPUS;SCHOOL:EAB:HRDEPT:16400505;SCHOOL:COMMUNITY:EMPLOYEE:BENEFITS:BASE;SCHOOL:COMMUNITY:EMPLOYEE:STAFF_ONLY;SCHOOL:SERVICES:SSLVPN:GENERAL:ALL;SCHOOL:COMMUNITY:TRANSPORTATION:ONCAMPUS", 
  "Shibboleth-mail": "Sample_Developer@school.edu", 
  "Shibboleth-persistent-id": "https://sso.college.edu/idp/shibboleth!https://server.college.edu/shibboleth-sp!sk1Z9qKruvXY7JXvsq4GRb8GCUk=", 
  "Shibboleth-sn": "Developer", 
  "Shibboleth-title": "Library Developer", 
  "Shibboleth-unscoped-affiliation": "member;staff"
}

settings.AUTHENTICATION_BACKENDS += (
    'django.contrib.auth.backends.RemoteUserBackend',
)

settings.MIDDLEWARE_CLASSES += (
    'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
)

settings.SHIBBOLETH_ATTRIBUTE_MAP = {
   "Shib-Identity-Provider": (True, "idp"),
   "Shibboleth-mail": (True, "email"),
   "Shibboleth-eppn": (True, "username"),
   "Shibboleth-schoolStatus": (True, "status"),
   "Shibboleth-affiliation": (True, "affiliation"),
   "Shib-Session-ID": (True, "session_id"),
   "Shibboleth-givenName": (True, "first_name"),
   "Shibboleth-sn": (True, "last_name"),
   "Shibboleth-mail": (True, "email"),
   "Shibboleth-schoolBarCode": (False, "barcode")
}

settings.ROOT_URLCONF = 'shibboleth.urls'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

class AttributesTest(unittest.TestCase):   
    def setUp(self):
        self.c = Client()
        
    def test_decorator_not_authenticated(self):
        """
        """
        resp = self.c.get('/')
        self.assertEqual(resp.status_code, 302)
        #Test the context - shouldn't exist
        self.assertEqual(resp.context, None) 
        
    def test_decorator_authenticated(self):
        """
        """
        resp = self.c.get('/', **SAMPLE_HEADERS)
        self.assertEqual(resp.status_code, 200)
        #Test the context
        user = resp.context.get('user')
        self.assertEqual(user.email, 'Sample_Developer@school.edu')
        self.assertTrue(user.is_authenticated())
        self.assertFalse(user.is_anonymous())
        
