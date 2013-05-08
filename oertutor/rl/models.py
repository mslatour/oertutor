from django.db import models

class QValue(models.Model):
    state = models.BigIntegerField(primary_key=True)
    action = models.IntegerField()
    reward = models.FloatField()
