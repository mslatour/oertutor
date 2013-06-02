from django.db import models
from concurrency.fields import AutoIncVersionField

class Action(models.Model):
    class Meta:
        abstract = True

class QValue(models.Model):
    state = models.BigIntegerField()
    action = models.IntegerField()
    value = models.FloatField()
    version = AutoIncVersionField() # to identify concurrency issues

    def __cmp__(self, other):
        return self.value.__cmp__(other)

    def __str__(self):
        return "<%d,%d,%f>" % (self.state, self.action, self.value)

    def __repr__(self):
        return self.__str__()
