from django.db import models
from oertutor.rl.models import Action as RLAction

class Student(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class OpenEducationalResource(RLAction):
    title = models.CharField(max_length=50)
    source = models.URLField()

class Exercise(models.Model):
    title = models.CharField(max_length=50)    

class ExerciseResult(models.Model):
    exercise = models.ForeignKey(Exercise)
    student = models.ForeignKey(Student)
