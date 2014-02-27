from oertutor.log.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver
from oertutor.tutor.models import Student, Trial
from oertutor.ga.models import Population
from oertutor.ga.signals import ga_next_generation

@receiver(post_save, sender=Student)
def log_student_model(sender, instance, **kwargs):
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
    if kwargs['created']:
        LogEntry.enter(
            entry={'class':'trial', 'pk':instance.pk,
                'action':'created', 'kc':instance.kc.pk},
            module="tutor/trial",
            student=instance.student
        )

@receiver(ga_next_generation)
def log_next_generation(sender, generation, **kwargs):
    LogEntry.enter(
        entry={'class':'population', 'pk': sender.pk,
            'action':'next_generation', 'generation': generation.pk},
        module="ga/population",
        student=None
    )
