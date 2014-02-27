from django.db import models
from oertutor.tutor.models import Student
import json

class LogEntry(models.Model):
    entry = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now=True)
    module = models.CharField(max_length=50)
    student = models.ForeignKey(Student, null=True)

    @staticmethod
    def enter(*args, **kwargs):
        if 'entry' in kwargs:
            if not isinstance(kwargs['entry'], str):
                try:
                    kwargs['entry'] = json.dumps(kwargs['entry'])
                except TypeError as e:
                    print e
                    print kwargs['entry']
        return LogEntry.objects.create(*args, **kwargs)
