from oertutor.log.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from oertutor.tutor.models import Student, Trial
from oertutor.ga.models import Population
from oertutor.tutor.signals import tutor_session_origin
from oertutor.ga.signals import *
from oertutor.settings import LOG_SIGNALS

@receiver(ga_err)
def log_error(sender, msg, location, **kwargs):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={
                "class": type(sender).__name__,
                "msg": msg, "location": location},
            module="ga/error",
            student=None
        )

@receiver(tutor_session_origin)
def log_session_origin(sender, origin, data, student, **kwargs):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={
                'origin': origin,
                'data': data},
            module='session/origin',
            student=student)

@receiver(post_save, sender=Student)
def log_student_model(sender, instance, **kwargs):
    if LOG_SIGNALS:
        if kwargs['update_fields'] is not None:
            if 'phase' in kwargs['update_fields']:
                LogEntry.enter(
                    entry={'class':'student', 'pk':instance.pk,
                    'action':'phase2'+instance.phase},
                    module="tutor/student",
                    student=instance
                )

@receiver(post_save, sender=Trial)
def log_trial_model(sender, instance, **kwargs):
    if LOG_SIGNALS:
        if kwargs['created']:
            LogEntry.enter(
                entry={'class':'trial', 'pk':instance.pk,
                    'action':'created', 'kc':instance.kc.pk},
                module="tutor/trial",
                student=instance.student
            )

@receiver(ga_next_generation)
def log_next_generation(sender, generation, **kwargs):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={'class':'population', 'pk': sender.pk,
                'action':'next_generation', 'generation': generation.pk},
            module="ga/population",
            student=None
        )

@receiver(ga_immigrate)
def log_immigrate(sender, generation, worst_individual, immigrant, **kwargs):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={'class':'population', 'pk': sender.pk,
                'action':'immigrate', 'generation': generation.pk,
                'worst_individual': worst_individual.pk, 'immigrant': immigrant.pk},
            module="ga/population",
            student=None
        )

@receiver(ga_bootstrap_evaluation)
def log_bootstrap(sender, generation, individual, bootstrap, **kwargs):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={'class':'population', 'pk': sender.pk,
                'action':'bootstrap', 'generation': generation.pk,
                'individual': individual.pk, 'bootstrap': bootstrap.pk,
                'value': str(bootstrap.value)},
            module="ga/population",
            student=None
        )

@receiver(ga_elite)
def log_elite(sender, generation, elite, **kwargs):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={'class':'population', 'pk': sender.pk,
                'action':'elite_preservation', 'generation': generation.pk,
                'elite': str([str(e.pk) for e in elite])},
            module="ga/population",
            student=None
        )
