"""
Semaphore (semaphore.co) SMS gateway integration.

Real API reference (https://semaphore.co/docs):
  POST https://api.semaphore.co/api/v4/messages
  Body (form-encoded, not JSON): apikey, number, message, sendername (optional)
  Response: JSON array, one object per recipient, e.g.:
    [{
      "message_id": 12345, "user_id": ..., "user": "...", "account_id": ...,
      "account": "...", "recipient": "639998887777", "message": "...",
      "sender_name": "...", "network": "Globe",
      "status": "Queued" | "Pending" | "Sent" | "Failed" | "Refunded",
      "type": "single", "source": "api",
      "created_at": "...", "updated_at": "..."
    }]

DRY RUN MODE (settings.SMS_DRY_RUN, default True): no HTTP call is made at
all. Nothing gets sent, nothing gets spent. This lets Dawn test the full
staging -> authorization -> send workflow end-to-end with zero cost and
zero credentials. Once she has a real SEMAPHORE_API_KEY, flipping
SMS_DRY_RUN=False in .env is the ONLY change needed to go live — no code
change, no redeploy of logic.
"""
import logging

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

SEMAPHORE_MESSAGES_ENDPOINT = 'https://api.semaphore.co/api/v4/messages'


def send_sms(recipient_number, message):
    """
    Sends a single SMS. Returns a dict:
      {'status': ..., 'recipient': ..., 'message': ..., 'gateway_response': ...}

    'status' is one of Semaphore's own values (Queued/Pending/Sent/Failed/
    Refunded) when live, or the literal string 'Simulated' in dry-run mode —
    the caller maps this to the app's DeliveryStatus choices.
    """
    dry_run = getattr(settings, 'SMS_DRY_RUN', True)

    if dry_run:
        timestamp = timezone.now().isoformat()
        logger.info(
            "[SMS DRY RUN] Would send to %s: %r (at %s)",
            recipient_number, message, timestamp,
        )
        return {
            'status': 'Simulated',
            'recipient': recipient_number,
            'message': message,
            'gateway_response': (
                f'DRY RUN — no request sent to Semaphore. Would have POSTed to '
                f'{SEMAPHORE_MESSAGES_ENDPOINT} at {timestamp}.'
            ),
        }

    api_key = getattr(settings, 'SEMAPHORE_API_KEY', '')
    if not api_key:
        logger.error("SMS_DRY_RUN is False but SEMAPHORE_API_KEY is not set — cannot send live SMS.")
        return {
            'status': 'Failed',
            'recipient': recipient_number,
            'message': message,
            'gateway_response': 'SEMAPHORE_API_KEY is not configured in .env.',
        }

    try:
        response = requests.post(
            SEMAPHORE_MESSAGES_ENDPOINT,
            data={
                'apikey': api_key,
                'number': recipient_number,
                'message': message,
                # 'sendername' intentionally omitted — no Sender Name registered
                # yet per Dawn; Semaphore falls back to the account's default.
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        # Semaphore always returns a JSON array, even for a single recipient.
        result = data[0] if isinstance(data, list) and data else {}
        return {
            'status': result.get('status', 'Pending'),
            'recipient': result.get('recipient', recipient_number),
            'message': result.get('message', message),
            'gateway_response': str(result),
        }
    except requests.RequestException as exc:
        logger.exception("Semaphore SMS send failed for %s", recipient_number)
        return {
            'status': 'Failed',
            'recipient': recipient_number,
            'message': message,
            'gateway_response': str(exc),
        }