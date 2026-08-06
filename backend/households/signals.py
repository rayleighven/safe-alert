from django.db.models.signals import post_save
from django.dispatch import receiver

from .cart_classifier import classify_household
from .models import VulnerabilityIndicator


@receiver(post_save, sender=VulnerabilityIndicator)
def update_household_priority(sender, instance, **kwargs):
    """
    Runs on every VulnerabilityIndicator save (Kagawad creating the initial
    hazard/structural assessment, or a BHW later updating health fields) so
    Household.evacuation_priority/priority_score always reflect the latest
    assessment — regardless of whether the save came through the API, the
    Django admin, or a shell script.
    """
    household = instance.household
    priority, score = classify_household(instance)
    household.evacuation_priority = priority
    household.priority_score = score
    household.save(update_fields=['evacuation_priority', 'priority_score', 'updated_at'])