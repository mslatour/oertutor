from django.db import models
from concurrency.fields import IntegerVersionField

class Action(models.Model):
    class Meta:
        abstract = True

class QValue(models.Model):
    version = IntegerVersionField() # to identify concurrency issues
    state = models.BigIntegerField(primary_key=True)
    action = models.IntegerField()
    value = models.FloatField()

    def __cmp__(self, other):
        return self.value.__cmp__(other)

    def __str__(self):
        return "<%s,%d,%f>" % (self.state, self.action, self.value)

    def __repr__(self):
        return self.__str__()
