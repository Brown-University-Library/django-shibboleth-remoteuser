from django.db import models
from django.contrib.sessions.models import Session


class ShibSession(models.Model):
    shib = models.CharField(max_length=100, primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
