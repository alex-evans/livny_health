"""
SOAP Mapping Service.

Parses clinical note text into structured SOAP (Subjective, Objective, Assessment, Plan) sections.
Uses keyword-based section detection without NLP dependencies.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal
import re


class Completeness(str, Enum):
    """Completeness status for SOAP sections."""
    EMPTY = "empty"
    PARTIAL = "partial"
    COMPLETE = "complete"


@dataclass
class SOAPSection:
    """A single SOAP section with content and completeness."""
    content: str
    completeness: Completeness
    word_count: int

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "completeness": self.completeness.value,
            "wordCount": self.word_count,
        }


@dataclass
class SOAPMapping:
    """Complete SOAP mapping result."""
    subjective: SOAPSection
    objective: SOAPSection
    assessment: SOAPSection
    plan: SOAPSection
    overall_completeness: Completeness

    def to_dict(self) -> dict:
        return {
            "subjective": self.subjective.to_dict(),
            "objective": self.objective.to_dict(),
            "assessment": self.assessment.to_dict(),
            "plan": self.plan.to_dict(),
            "overallCompleteness": self.overall_completeness.value,
        }


# Section markers for keyword-based detection
# Each section has multiple possible markers (case-insensitive)
SECTION_MARKERS: dict[str, list[str]] = {
    "subjective": [
        "subjective:",
        "subjective",
        "s:",
        "hpi:",
        "hpi",
        "history of present illness:",
        "history of present illness",
        "chief complaint:",
        "chief complaint",
        "cc:",
        "patient reports",
        "patient states",
        "patient complains",
        "patient presents",
        "presenting complaint",
    ],
    "objective": [
        "objective:",
        "objective",
        "o:",
        "physical exam:",
        "physical exam",
        "physical examination:",
        "physical examination",
        "pe:",
        "exam:",
        "vitals:",
        "vitals",
        "on exam",
        "on examination",
        "findings:",
        "examination reveals",
    ],
    "assessment": [
        "assessment:",
        "assessment",
        "a:",
        "impression:",
        "impression",
        "diagnosis:",
        "diagnosis",
        "dx:",
        "assessment/plan:",
        "clinical impression",
        "working diagnosis",
        "differential:",
        "differential diagnosis",
    ],
    "plan": [
        "plan:",
        "plan",
        "p:",
        "recommendations:",
        "recommendations",
        "treatment plan:",
        "treatment plan",
        "follow-up:",
        "follow up:",
        "follow-up",
        "orders:",
        "orders",
        "next steps:",
        "management:",
        "management plan",
        "disposition:",
        "rx:",
        "prescriptions:",
    ],
}

# Word count thresholds for completeness
EMPTY_THRESHOLD = 0  # 0 words = empty
PARTIAL_THRESHOLD = 30  # 1-29 words = partial, 30+ = complete


def _count_words(text: str) -> int:
    """Count words in text."""
    if not text or not text.strip():
        return 0
    return len(text.split())


def _get_completeness(word_count: int) -> Completeness:
    """Determine completeness based on word count."""
    if word_count <= EMPTY_THRESHOLD:
        return Completeness.EMPTY
    elif word_count < PARTIAL_THRESHOLD:
        return Completeness.PARTIAL
    else:
        return Completeness.COMPLETE


def _find_section_start(text: str, markers: list[str]) -> int | None:
    """
    Find the start position of a section based on markers.
    Returns the position after the marker, or None if not found.
    """
    text_lower = text.lower()
    best_pos = None

    for marker in markers:
        marker_lower = marker.lower()
        pos = text_lower.find(marker_lower)
        if pos != -1:
            # Found a marker - use position after the marker
            end_pos = pos + len(marker)
            # Skip any following colon or whitespace
            while end_pos < len(text) and text[end_pos] in ": \t":
                end_pos += 1
            if best_pos is None or pos < best_pos:
                best_pos = end_pos

    return best_pos


def _extract_section_content(
    text: str,
    section_name: str,
    all_markers: dict[str, list[str]],
) -> str:
    """
    Extract content for a specific section.
    Content starts at the section marker and ends at the next section marker.
    """
    markers = all_markers[section_name]
    start = _find_section_start(text, markers)

    if start is None:
        return ""

    # Find where this section ends (start of next section)
    end = len(text)
    for other_section, other_markers in all_markers.items():
        if other_section == section_name:
            continue
        other_start = _find_section_start(text, other_markers)
        if other_start is not None and other_start > start:
            # Found a subsequent section - but we need to find its marker position,
            # not where content starts
            for marker in other_markers:
                marker_lower = marker.lower()
                marker_pos = text.lower().find(marker_lower)
                if marker_pos is not None and marker_pos > start and marker_pos < end:
                    end = marker_pos

    content = text[start:end].strip()
    return content


def _infer_sections_without_markers(text: str) -> dict[str, str]:
    """
    Attempt to infer SOAP sections from unstructured text.
    Uses heuristics based on common patterns when explicit markers aren't present.
    """
    sections = {
        "subjective": "",
        "objective": "",
        "assessment": "",
        "plan": "",
    }

    if not text or not text.strip():
        return sections

    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    if not paragraphs:
        return sections

    # Simple heuristic: assign paragraphs based on position and content
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        line_lower = line.lower()

        # Check for medication/prescription patterns (plan)
        if any(
            pattern in line_lower
            for pattern in [
                "mg",
                "daily",
                "twice",
                "prn",
                "refill",
                "prescribe",
                "start",
                "continue",
                "increase",
                "decrease",
                "taper",
            ]
        ):
            sections["plan"] += line + "\n"

        # Check for vital signs / exam findings (objective)
        elif any(
            pattern in line_lower
            for pattern in [
                "bp:",
                "bp ",
                "hr:",
                "hr ",
                "temp:",
                "temp ",
                "rr:",
                "weight:",
                "height:",
                "bmi:",
                "lungs",
                "heart",
                "abdomen",
                "neurological",
                "extremities",
                "skin",
                "heent",
                "no acute distress",
                "alert and oriented",
                "mmhg",
                "bpm",
            ]
        ):
            sections["objective"] += line + "\n"

        # Check for diagnosis/assessment patterns
        elif any(
            pattern in line_lower
            for pattern in [
                "diagnosis",
                "icd",
                "likely",
                "suspect",
                "consistent with",
                "rule out",
                "r/o",
                "probable",
                "possible",
            ]
        ):
            sections["assessment"] += line + "\n"

        # Check for subjective/history patterns
        elif any(
            pattern in line_lower
            for pattern in [
                "patient",
                "reports",
                "denies",
                "complains",
                "history",
                "symptoms",
                "pain",
                "days",
                "weeks",
                "started",
                "worse",
                "better",
            ]
        ):
            sections["subjective"] += line + "\n"

    # Trim all sections
    for key in sections:
        sections[key] = sections[key].strip()

    return sections


class SOAPMappingService:
    """Service for parsing clinical notes into SOAP sections."""

    def parse(self, content: str) -> SOAPMapping:
        """
        Parse clinical note content into SOAP sections.

        Args:
            content: The raw clinical note text

        Returns:
            SOAPMapping with structured sections and completeness indicators
        """
        if not content or not content.strip():
            empty_section = SOAPSection(
                content="",
                completeness=Completeness.EMPTY,
                word_count=0,
            )
            return SOAPMapping(
                subjective=empty_section,
                objective=empty_section,
                assessment=empty_section,
                plan=empty_section,
                overall_completeness=Completeness.EMPTY,
            )

        # First try to extract sections using explicit markers
        sections = {}
        has_explicit_markers = False

        for section_name in ["subjective", "objective", "assessment", "plan"]:
            section_content = _extract_section_content(
                content, section_name, SECTION_MARKERS
            )
            sections[section_name] = section_content
            if section_content:
                has_explicit_markers = True

        # If no explicit markers found, try to infer sections
        if not has_explicit_markers:
            sections = _infer_sections_without_markers(content)

        # Build SOAP sections with completeness
        soap_sections = {}
        completeness_values = []

        for section_name in ["subjective", "objective", "assessment", "plan"]:
            section_content = sections[section_name]
            word_count = _count_words(section_content)
            completeness = _get_completeness(word_count)
            completeness_values.append(completeness)

            soap_sections[section_name] = SOAPSection(
                content=section_content,
                completeness=completeness,
                word_count=word_count,
            )

        # Calculate overall completeness
        if all(c == Completeness.COMPLETE for c in completeness_values):
            overall = Completeness.COMPLETE
        elif all(c == Completeness.EMPTY for c in completeness_values):
            overall = Completeness.EMPTY
        else:
            overall = Completeness.PARTIAL

        return SOAPMapping(
            subjective=soap_sections["subjective"],
            objective=soap_sections["objective"],
            assessment=soap_sections["assessment"],
            plan=soap_sections["plan"],
            overall_completeness=overall,
        )
