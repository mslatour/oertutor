from django.db import models
from oertutor.ga.models import Gene, Individual, Population

class Student(models.Model):
    NEW = 'new'
    PRETEST = 'pre'
    SEQUENCE = 'seq'
    POSTTEST = 'post'
    DONE = 'done'
    PHASES = (
        (NEW, 'New'),
        (PRETEST, 'Pre-test'),
        (SEQUENCE, 'Sequence'),
        (POSTTEST, 'Post-test'),
        (DONE, 'Done')
    )
    phase = models.CharField(max_length=4, choices=PHASES, default=NEW)
    started = models.DateTimeField(auto_now_add=True)
    pretest = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    population = models.ForeignKey(Population, null=True, related_name='+')
    sequence = models.ForeignKey(Individual, null=True, related_name='+')
    posttest = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def by_session(session):
        if session.get('student', None) is not None:
            try:
                return Student.objects.get(pk=session['student'])
            except Student.DoesNotExist:
                del session['student']
                return Student.by_session(session)
        else:
            student = Student.objects.create()
            session['student'] = student.pk
            return student

class Curriculum(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Curricula"

class KnowledgeComponent(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    pretest = models.ForeignKey('Test', related_name = '+')
    posttest = models.ForeignKey('Test', related_name = '+')
    curriculum = models.ForeignKey(Curriculum, related_name='kcs')
    antecedents = models.ManyToManyField('self', null=True, blank=True,
            symmetrical=False, related_name='consequent')

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

class StudentCategory(Population):
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Student Category"
        verbose_name_plural = "Student Categories"

class Trial(models.Model):
    kc = models.ForeignKey('KnowledgeComponent')
    student = models.ForeignKey('Student')
    pretest_result = models.ForeignKey('TestResult', related_name='+')
    sequence = models.ForeignKey(Individual, null=True, related_name='+')
    posttest_result = models.ForeignKey('TestResult', related_name='+')
    category = models.ForeignKey('StudentCategory', null=True)
    datetime = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = "Knowledge Component Explanation"

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

class Test(models.Model):
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField('Question', related_name='test')

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

class Question(models.Model):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.question[:50]

    def __repr__(self):
        return self.question[:10]

class TestResult(models.Model):
    test = models.ForeignKey('Test', related_name='results')
    student = models.ForeignKey('Student')
    score = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    datetime = models.DateTimeField(auto_now = True)

class StudentAnswers(models.Model):
    question = models.ForeignKey('Question')
    testresult = models.ForeignKey('TestResult', related_name='answers')
    student = models.ForeignKey('Student')
    answer = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now = True)
