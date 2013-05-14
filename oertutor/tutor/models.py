from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class Exercise(models.Model):
    title = models.CharField(max_length=50)    

class ExerciseResult(models.Model):
    exercise = models.ForeignKey(Exercise)
    student = models.ForeignKey(Student)
