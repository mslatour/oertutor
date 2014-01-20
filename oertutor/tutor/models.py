from django.db import models
from oertutor.ga.models import Gene

class Student(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class Curriculum(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()

class KnowledgeComponent(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    curriculum = models.ForeignKey(Curriculum, related_name='kcs')
    antecedents = models.ManyToManyField('self', null=True,
            symmetrical=False, related_name='consequent')

class Resource(Gene):
    title = models.CharField(max_length=50)
    source = models.URLField()
    kc = models.ForeignKey(KnowledgeComponent, related_name='resources')

class Exercise(Resource):
    params = models.CharField(max_length=255)

class ExerciseResult(models.Model):
    exercise = models.ForeignKey(Exercise, related_name='result')
    student = models.ForeignKey(Student)
    data = models.TextField()

class Observation(models.Model):
    handle = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now = True)
