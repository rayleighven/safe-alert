from django.db import models


class UserRole(models.TextChoices):
    BARANGAY_SECRETARY = 'Barangay Secretary', 'Barangay Secretary'
    MDRRMO_OFFICER = 'MDRRMO Officer', 'MDRRMO Officer'
    BDRRMC_CHAIRPERSON = 'BDRRMC Chairperson', 'BDRRMC Chairperson'
    BARANGAY_KAGAWAD_TANOD = 'Barangay Kagawad/Tanod', 'Barangay Kagawad/Tanod'
    BARANGAY_HEALTHWORKER = 'Barangay Healthworker', 'Barangay Healthworker'
    RESIDENT = 'Resident', 'Resident'


class StaffRole(models.TextChoices):
    """Subset of UserRole used for Emergency_Contacts (excludes Resident)."""
    BARANGAY_SECRETARY = 'Barangay Secretary', 'Barangay Secretary'
    MDRRMO_OFFICER = 'MDRRMO Officer', 'MDRRMO Officer'
    BDRRMC_CHAIRPERSON = 'BDRRMC Chairperson', 'BDRRMC Chairperson'
    BARANGAY_KAGAWAD_TANOD = 'Barangay Kagawad/Tanod', 'Barangay Kagawad/Tanod'
    BARANGAY_HEALTHWORKER = 'Barangay Healthworker', 'Barangay Healthworker'


class UserStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'
    ARCHIVED = 'Archived', 'Archived'


class Priority(models.TextChoices):
    HIGH = 'High', 'High'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'


class CenterStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'
    UNDER_MAINTENANCE = 'Under Maintenance', 'Under Maintenance'


class HazardType(models.TextChoices):
    FLOOD = 'Flood', 'Flood'
    STORM_SURGE = 'Storm Surge', 'Storm Surge'
    LANDSLIDE = 'Landslide', 'Landslide'
    EARTHQUAKE = 'Earthquake', 'Earthquake'


class DisasterType(models.TextChoices):
    FLOOD = 'Flood', 'Flood'
    STORM_SURGE = 'Storm Surge', 'Storm Surge'
    LANDSLIDE = 'Landslide', 'Landslide'
    EARTHQUAKE = 'Earthquake', 'Earthquake'
    FIRE = 'Fire', 'Fire'
    OTHER = 'Other', 'Other'


class DisasterStatus(models.TextChoices):
    ONGOING = 'Ongoing', 'Ongoing'
    RESOLVED = 'Resolved', 'Resolved'


class HouseMaterial(models.TextChoices):
    CONCRETE = 'Concrete', 'Concrete'
    MIXED = 'Mixed', 'Mixed'
    LIGHT = 'Light', 'Light'
    SALVAGED = 'Salvaged', 'Salvaged'


class RoofMaterial(models.TextChoices):
    GI_SHEET = 'GI Sheet', 'GI Sheet'
    COGON = 'Cogon', 'Cogon'
    MIXED = 'Mixed', 'Mixed'
    CONCRETE = 'Concrete', 'Concrete'


class Sex(models.TextChoices):
    MALE = 'Male', 'Male'
    FEMALE = 'Female', 'Female'


class EntryStatus(models.TextChoices):
    CHECKED_IN = 'Checked-in', 'Checked-in'
    DEPARTED = 'Departed', 'Departed'


class AnnouncementCategoryTag(models.TextChoices):
    ADVISORY = 'Advisory', 'Advisory'
    ALERT = 'Alert', 'Alert'
    INFORMATIONAL = 'Informational', 'Informational'
    EMERGENCY = 'Emergency', 'Emergency'


class RecipientType(models.TextChoices):
    ALL = 'All', 'All'
    HIGH_PRIORITY = 'High Priority', 'High Priority'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'
    CUSTOM = 'Custom', 'Custom'


class SMSStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    SENT = 'Sent', 'Sent'
    PARTIALLY_SENT = 'Partially Sent', 'Partially Sent'
    FAILED = 'Failed', 'Failed'


class DeliveryStatus(models.TextChoices):
    DELIVERED = 'Delivered', 'Delivered'
    FAILED = 'Failed', 'Failed'
    PENDING = 'Pending', 'Pending'


class AuditAction(models.TextChoices):
    CREATE = 'Create', 'Create'
    UPDATE = 'Update', 'Update'
    ARCHIVE = 'Archive', 'Archive'
    RESTORE = 'Restore', 'Restore'
    LOGIN = 'Login', 'Login'