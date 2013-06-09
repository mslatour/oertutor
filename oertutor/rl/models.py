from django.db import models
from concurrency.fields import AutoIncVersionField

class Action(models.Model):
    class Meta:
        abstract = True

class QValue(models.Model):
    state = models.BigIntegerField()
    state_desc = models.CharField(max_length=100)
    action = models.IntegerField()
    value = models.FloatField()
    label = models.CharField(max_length=25)
    version = AutoIncVersionField() # to identify concurrency issues

    def __cmp__(self, other):
        return self.value.__cmp__(other)

    def __str__(self):
        return "<%d,%d,%f>" % (self.state_desc, self.action, self.value)

    def __repr__(self):
        return self.__str__()
