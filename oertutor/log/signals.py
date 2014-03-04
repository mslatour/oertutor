from oertutor.log.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from oertutor.tutor.models import Student, Trial
from oertutor.ga.models import Population
from oertutor.ga.signals import ga_next_generation, ga_immigrate
from oertutor.settings import LOG_SIGNALS

err = Signal(providing_args=["msg","location"])

@receiver(err)
def log_error(sender, msg, location):
    if LOG_SIGNALS:
        LogEntry.enter(
            entry={"class": type(sender), "msg": msg, "location": location},
            module="error"
            student=None
        )

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
