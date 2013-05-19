from django.db import models

class Action(models.Model):
    class Meta:
        abstract = True

class QValue(models.Model):
    state = models.BigIntegerField(primary_key=True)
    action = models.IntegerField()
    reward = models.FloatField()
