"""
Encounter Prompt resource package.

Provides models and repository for encounter prompts that guide physicians
through clinical encounters.
"""

from .model import (
    EncounterPrompt,
    PromptGenerationResult,
    PromptType,
    PromptStatus,
    ViewerSection,
    AlertLevel,
)
from .repository import EncounterPromptRepository

__all__ = [
    "EncounterPrompt",
    "PromptGenerationResult",
    "PromptType",
    "PromptStatus",
    "ViewerSection",
    "AlertLevel",
    "EncounterPromptRepository",
]
