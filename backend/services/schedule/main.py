"""
This module provides functions to manage schedule data.
"""

from datetime import datetime

from .fake_data import generate_appointments_for_date, FAKE_PROVIDERS


def get_daily_schedule(date_str: str, provider_id: str = "provider-001") -> dict:
    """
    Get the daily schedule for a provider on a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format
        provider_id: The provider ID (defaults to provider-001)

    Returns:
        Dictionary containing the daily schedule
    """
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

    provider = FAKE_PROVIDERS.get(provider_id)
    if not provider:
        return None

    appointments = generate_appointments_for_date(date_str)

    return {
        "date": date_str,
        "providerId": provider["id"],
        "providerName": provider["name"],
        "appointments": appointments,
    }
