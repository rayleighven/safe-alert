from django.db.models.signals import post_save
from django.dispatch import receiver

from .cart_classifier import classify_household
from .models import HouseholdMember, VulnerabilityIndicator


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


@receiver(post_save, sender=HouseholdMember)
def refresh_indicator_on_member_change(sender, instance, **kwargs):
    """
    has_senior_citizen/has_pwd/has_pregnant_member/has_child on the latest
    indicator are derived from household members (VulnerabilityIndicator.save()),
    so adding, editing, or archiving (soft-delete via save()) a member has to
    refresh the latest indicator to keep those fields — and the downstream
    CART classification triggered by update_household_priority above — in sync.
    """
    indicator = instance.household.vulnerability_indicators.filter(is_archived=False).order_by('-assessed_at').first()
    if indicator:
        indicator.save()