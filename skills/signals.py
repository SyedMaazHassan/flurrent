from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from skills.models import Quiz

@receiver(post_save, sender=Quiz)
def create_quiz(sender, instance, created, **kwargs):
    if created:
        skill = instance.skill
        skill.quiz_added += 1
        skill.save()
        # do something here


@receiver(post_delete, sender=Quiz)
def delete_quiz(sender, instance, **kwargs):
    # do something here when a quiz object is deleted
    skill = instance.skill
    skill.quiz_added -= 1
    skill.save()