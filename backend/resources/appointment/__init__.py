"""
Appointment resource package.
"""

from .model import Appointment, AppointmentStatus, AppointmentParticipant, AppointmentFlag
from .repository import AppointmentRepository

__all__ = [
    "Appointment",
    "AppointmentStatus",
    "AppointmentParticipant",
    "AppointmentFlag",
    "AppointmentRepository",
]
