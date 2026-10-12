from datetime import timedelta
import secrets

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import AuditLog, User
from announcements.models import Announcement, AnnouncementCategory, SMSLog, SMSNotification
from core.choices import (
    AnnouncementCategoryTag,
    CenterStatus,
    DeliveryStatus,
    HouseMaterial,
    HazardType,
    Priority,
    RecipientType,
    RoofMaterial,
    SMSStatus,
    Sex,
    UserRole,
    UserStatus,
)
from evacuation_centers.models import EvacuationCenter
from households.models import Household, HouseholdMember, VulnerabilityIndicator
from maps.models import HazardMap


PRIORITIES = [
    Priority.HIGH, Priority.HIGH, Priority.HIGH,
    Priority.MEDIUM, Priority.MEDIUM, Priority.MEDIUM, Priority.MEDIUM,
    Priority.LOW, Priority.LOW, Priority.LOW,
]
HOUSEHOLD_MEMBERS = [4, 4, 4, 5, 2, 3, 4, 2, 5, 3]


class Command(BaseCommand):
    help = 'Adds 10 clearly labeled demo residents and dashboard records for local preview.'

    def add_arguments(self, parser):
        parser.add_argument('--barangay', help='Barangay name for the demo records (defaults to the first active Secretary account).')
        parser.add_argument('--clear', action='store_true', help='Remove only records created by this demo seeder.')
        parser.add_argument('--reset-passwords', action='store_true', help='Generate and print new passwords for the 10 demo residents.')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Refusing to seed demo data unless DJANGO_DEBUG is enabled.')
        if options['clear']:
            self._clear_demo_data()
            self.stdout.write(self.style.SUCCESS('Dashboard demo records and demo resident accounts were removed.'))
            return

        secretary_query = User.objects.filter(
            role=UserRole.BARANGAY_SECRETARY,
            status=UserStatus.ACTIVE,
            barangay__isnull=False,
        )
        if options['barangay']:
            secretary_query = secretary_query.filter(barangay__name__iexact=options['barangay'].strip())
        encoder = secretary_query.select_related('barangay').order_by('username').first()
        if not encoder:
            requested_barangay = f" for {options['barangay']}" if options['barangay'] else ''
            raise CommandError(
                f'Create an active Barangay Secretary account linked to a barangay{requested_barangay} first, '
                'then run this command again.'
            )
        barangay = encoder.barangay

        with transaction.atomic():
            self.generated_credentials = []
            households = self._seed_households(barangay, encoder, options['reset_passwords'])
            self._seed_centers(barangay, encoder)
            self._seed_maps(barangay, encoder)
            self._seed_announcements(barangay, encoder)
            self._seed_sms(barangay, encoder, households)

        self.stdout.write(self.style.SUCCESS(
            f'Dashboard demo data is ready for {barangay.name}: '
            '10 resident accounts, 10 households, vulnerability assessments, '
            '3 evacuation centers, 3 NOAH map references, 2 announcements, and SMS delivery records.'
        ))
        if self.generated_credentials:
            self.stdout.write('New local demo login credentials (do not commit or share these):')
            for username, password in self.generated_credentials:
                self.stdout.write(f'{username}: {password}')
        else:
            self.stdout.write('Demo resident usernames: demo_resident_01 through demo_resident_10')
            self.stdout.write('Existing demo passwords were left unchanged. Use --reset-passwords to generate and display new ones.')

    def _clear_demo_data(self):
        with transaction.atomic():
            SMSNotification.objects.filter(subject='DEMO: Sample delivery summary').delete()
            Announcement.objects.filter(title__startswith='DEMO:').delete()
            HazardMap.objects.filter(map_title__startswith='Demo Project NOAH ').delete()
            EvacuationCenter.objects.filter(name__startswith='Demo ').delete()
            Household.objects.filter(household_number__startswith='DEMO-').delete()
            for index in range(1, 11):
                user = User.objects.filter(
                    username=f'demo_resident_{index:02d}',
                    email=f'demo_resident_{index:02d}@example.invalid',
                    role=UserRole.RESIDENT,
                ).first()
                if user:
                    AuditLog.objects.filter(user=user).delete()
                    user.delete()

    def _seed_households(self, barangay, encoder, reset_passwords):
        households = []
        now = timezone.now()
        for index, priority in enumerate(PRIORITIES, start=1):
            username = f'demo_resident_{index:02d}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': f'Demo Resident {index:02d}',
                    'email': f'{username}@example.invalid',
                    'role': UserRole.RESIDENT,
                    'barangay': barangay,
                    'status': UserStatus.ACTIVE,
                },
            )
            if created:
                password = secrets.token_urlsafe(24)
                user.set_password(password)
                user.save(update_fields=['password'])
                self.generated_credentials.append((username, password))
            elif user.role != UserRole.RESIDENT:
                raise CommandError(f'{username} already exists but is not a Resident account.')
            elif reset_passwords:
                password = secrets.token_urlsafe(24)
                user.set_password(password)
                user.save(update_fields=['password'])
                self.generated_credentials.append((username, password))

            household, _ = Household.objects.update_or_create(
                household_number=f'DEMO-{index:04d}',
                defaults={
                    'barangay': barangay,
                    'head_of_family': f'Demo Family {index:02d}',
                    'contact_number': f'000000{index:04d}',
                    'address': f'Demo address {index}, {barangay.name}, Baclayon, Bohol',
                    'purok': f'Purok {((index - 1) % 5) + 1}',
                    'total_members': HOUSEHOLD_MEMBERS[index - 1],
                    'evacuation_priority': priority,
                    'priority_score': [91, 86, 82, 74, 70, 66, 61, 42, 35, 28][index - 1],
                    'encoded_by': encoder,
                    'resident_user': user,
                    'is_archived': False,
                    'archived_at': None,
                },
            )
            households.append(household)

            for member_index in range(HOUSEHOLD_MEMBERS[index - 1]):
                age = [72, 45, 28, 12, 8][member_index % 5] if index <= 3 else [72, 43, 15, 8, 29][(index + member_index) % 5]
                HouseholdMember.objects.update_or_create(
                    household=household,
                    full_name=f'Demo Member {index:02d}-{member_index + 1:02d}',
                    defaults={
                        'age': age,
                        'sex': Sex.FEMALE if member_index in (2, 4) else Sex.MALE,
                        'relationship': 'Head' if member_index == 0 else 'Family member',
                        'occupation': 'Demo record',
                        'is_senior_citizen': age >= 60,
                        'is_child': age < 18,
                        'is_pwd': (index <= 3 and member_index == 1) or (index in (6, 8) and member_index == 0),
                        'is_pregnant': (index <= 3 and member_index == 2) or (index == 4 and member_index == 0),
                        'is_archived': False,
                        'archived_at': None,
                    },
                )

            VulnerabilityIndicator.objects.update_or_create(
                household=household,
                defaults={
                    'house_material': HouseMaterial.SALVAGED if index <= 3 else HouseMaterial.MIXED,
                    'roof_material': RoofMaterial.COGON if index <= 3 or index % 3 == 0 else RoofMaterial.GI_SHEET,
                    'flood_prone': index <= 3 or index % 2 == 0,
                    'storm_surge_prone': index <= 3 or index in (4, 8),
                    'landslide_prone': index <= 3 or index == 6,
                    'coastal_zone': index <= 3 or index in (4, 8),
                    'assessed_by': encoder,
                    'is_archived': False,
                    'archived_at': None,
                },
            )
        return households

    def _seed_centers(self, barangay, encoder):
        for name, address, capacity, occupancy in [
            ('Demo Community Hall', 'Purok 1, demo site', 120, 78),
            ('Demo Elementary School', 'Purok 3, demo site', 200, 116),
            ('Demo Covered Court', 'Purok 5, demo site', 80, 19),
        ]:
            EvacuationCenter.objects.update_or_create(
                barangay=barangay,
                name=name,
                defaults={
                    'address': address,
                    'capacity': capacity,
                    'current_occupancy': occupancy,
                    'status': CenterStatus.ACTIVE,
                    'contact_person': 'Demo Coordinator',
                    'contact_number': '0000000000',
                    'managed_by': encoder,
                    'is_archived': False,
                    'archived_at': None,
                },
            )

    def _seed_maps(self, barangay, encoder):
        for hazard in (HazardType.FLOOD, HazardType.STORM_SURGE, HazardType.LANDSLIDE):
            HazardMap.objects.update_or_create(
                barangay=barangay,
                map_title=f'Demo Project NOAH {hazard} reference',
                defaults={
                    'hazard_type': hazard,
                    'source': 'Project NOAH',
                    'map_url': '',
                    'description': f'Demo-only {hazard.lower()} map entry for dashboard preview.',
                    'uploaded_by': encoder,
                    'is_archived': False,
                    'archived_at': None,
                },
            )

    def _seed_announcements(self, barangay, encoder):
        now = timezone.now()
        items = [
            ('DEMO: Heavy rain preparedness advisory', 'This is sample dashboard content. Check local advisories and prepare essential supplies.', AnnouncementCategoryTag.ADVISORY),
            ('DEMO: Evacuation readiness notice', 'This sample alert is for local dashboard preview only. It is not an active emergency notice.', AnnouncementCategoryTag.ALERT),
        ]
        for title, body, category in items:
            announcement, _ = Announcement.objects.update_or_create(
                barangay=barangay,
                title=title,
                defaults={
                    'body': body,
                    'is_public': True,
                    'posted_by': encoder,
                    'published_at': now,
                    'expires_at': now + timedelta(days=30),
                    'is_archived': False,
                    'archived_at': None,
                },
            )
            AnnouncementCategory.objects.update_or_create(
                announcement=announcement,
                category=category,
            )

    def _seed_sms(self, barangay, encoder, households):
        now = timezone.now()
        notification, _ = SMSNotification.objects.update_or_create(
            barangay=barangay,
            subject='DEMO: Sample delivery summary',
            defaults={
                'message_body': 'Demo-only SMS delivery data. No messages were sent.',
                'recipient_type': RecipientType.ALL,
                'total_recipients': len(households),
                'sent_count': 8,
                'failed_count': 2,
                'status': SMSStatus.PARTIALLY_SENT,
                'initiated_by': encoder,
                'sent_at': now,
                'is_archived': False,
                'archived_at': None,
            },
        )
        statuses = [DeliveryStatus.DELIVERED] * 7 + [DeliveryStatus.FAILED] * 2 + [DeliveryStatus.SIMULATED]
        for household, status in zip(households, statuses):
            SMSLog.objects.update_or_create(
                sms=notification,
                household=household,
                defaults={
                    'contact_number': household.contact_number,
                    'delivery_status': status,
                    'gateway_response': 'Demo record; no SMS was sent.',
                    'sent_at': now,
                    'is_archived': False,
                    'archived_at': None,
                },
            )
