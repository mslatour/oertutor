from django.db import models
from django import forms
from oertutor.ga.models import Gene, Individual, Population, Evaluation

class Student(models.Model):
    NEW = 'new'
    INTRO = 'intr'
    PRETEST = 'pre'
    SEQUENCE = 'seq'
    POSTTEST = 'post'
    SKIP = 'skip'
    EXAM = 'exam'
    DONE = 'done'
    PHASES = (
        (NEW, 'New'),
        (INTRO, 'Introduction'),
        (PRETEST, 'Pre-test'),
        (SEQUENCE, 'Sequence'),
        (POSTTEST, 'Post-test'),
        (SKIP, 'Skipped'),
        (EXAM, 'Final exam'),
        (DONE, 'Done')
    )
    phase = models.CharField(max_length=4, choices=PHASES, default=NEW)
    started = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    preskill = models.SmallIntegerField(null=True, blank=True)
    postskill = models.SmallIntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

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

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return "Student [%s] %s" % (self.phase, self.started)

    def __repr__(self):
        return "Student[%s]" % (self.phase,)


class Curriculum(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    exam = models.ForeignKey('Test', related_name='+', null=True)

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
    kc = models.ForeignKey('KnowledgeComponent', related_name='+')
    lower_score = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    upper_score = models.DecimalField(default=1.0, max_digits=4, decimal_places=2)

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
    curriculum = models.ForeignKey('Curriculum', related_name='+')
    student = models.ForeignKey('Student', related_name='trials')
    pretest_result = models.ForeignKey('TestResult', related_name='+',
            null=True)
    sequence = models.ForeignKey(Individual, null=True, related_name='+')
    sequence_position = models.SmallIntegerField(default=0)
    posttest_result = models.ForeignKey('TestResult', related_name='+',
            null=True)
    evaluation = models.ForeignKey(Evaluation, null=True, related_name='+')
    category = models.ForeignKey('StudentCategory', null=True)
    datetime = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = "Knowledge Component Explanation"

class BootstrapEvaluation(models.Model):
    sequence = models.CharField(max_length=255)
    category = models.ForeignKey('StudentCategory', related_name='+')
    trial = models.ForeignKey(Trial, null=True, related_name='+')
    value = models.DecimalField(null=True, max_digits=10, decimal_places=9)
    used = models.BooleanField(default=False)

class Resource(Gene):
    title = models.CharField(max_length=50)
    source = models.URLField()
    kc = models.ForeignKey(KnowledgeComponent, related_name='resources')

    @staticmethod
    def factory(kc, **kwargs):
        resource, created = Resource.objects.get_or_create(kc=kc, **kwargs)
        for category in StudentCategory.objects.filter(kc=kc):
            category.pool.add(resource)
            category.save()
        return resource

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

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
    template = models.CharField(max_length=255, null=True, blank=True)
    questions = models.ManyToManyField('Question', related_name='test',
            null=True, blank=True)

    def grade(self, answers, student):
        score = 0.0
        weights = 0
        result = TestResult.objects.create(test=self, student=student)
        for question in self.questions.all():
            weights += question.weight
            answer = answers.get(question.handle, "")
            StudentAnswer.objects.create(question=question, testresult=result,
                student=student, answer=answer)
            if question.downcast().correct(answer):
                score += question.weight
        score /= weights
        result.score = score
        result.save()
        return result

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

class Question(models.Model):
    handle = models.CharField(max_length=50)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    weight = models.SmallIntegerField(default=1)
    template = models.CharField(max_length=255,
            default='question/generic.html')

    @staticmethod
    def factory(**kwargs):
        q, created = Question.objects.get_or_create(**kwargs)
        return q

    def correct(self, answer):
        return self.answer == answer

    def downcast(self):
        try:
            return self.nimquestion
        except NimQuestion.DoesNotExist:
            pass
        try:
            return self.multiplechoicequestion
        except MultipleChoiceQuestion.DoesNotExist:
            pass
        return self

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.question[:50]

    def __repr__(self):
        return self.question[:10]

class NimQuestion(Question):

    @staticmethod
    def factory(**kwargs):
        q, created = NimQuestion.objects.get_or_create(**kwargs)
        return q

    def correct(self, answer):
        import re
        regex = re.compile("^.*\[1\][^,]+$")
        return regex.match(answer) is not None

class MultipleChoiceQuestion(Question):
    answers = models.ManyToManyField('Answer', related_name='+')

    def __init__(self, *args, **kwargs):
        if 'template' not in kwargs:
            kwargs['template'] = 'question/multiplechoice.html'
        super(MultipleChoiceQuestion, self).__init__(*args, **kwargs)

    @staticmethod
    def factory(answer_list={}, **kwargs):
        q, created = MultipleChoiceQuestion.objects.get_or_create(**kwargs)
        for answer in answer_list:
            q.answers.add(Answer.objects.create(handle=answer[0],
                body=answer[1]))
        q.save()
        return q

class Answer(models.Model):
    handle = models.CharField(max_length=50)
    body = models.CharField(max_length=255)

class TestResult(models.Model):
    test = models.ForeignKey('Test', related_name='results')
    student = models.ForeignKey('Student')
    score = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    datetime = models.DateTimeField(auto_now = True)

class StudentAnswer(models.Model):
    question = models.ForeignKey('Question')
    testresult = models.ForeignKey('TestResult', related_name='answers')
    student = models.ForeignKey('Student')
    answer = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now = True)
