"""Tests for encounter prompt service."""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from resources import (
    Patient,
    PatientRepository,
    Encounter,
    EncounterRepository,
    EncounterStatus,
    ClinicalAlertRepository,
    MedicationRequest,
)
from resources.core import HumanName, Reference
from resources.encounter_prompt import (
    EncounterPrompt,
    EncounterPromptRepository,
    PromptStatus,
)
from resources.patient import Problem, ProblemStatus
from services.encounter_prompt_service import (
    EncounterPromptService,
    EncounterPromptServiceBuilder,
    EncounterNotFoundError,
    PromptNotFoundError,
    PromptNotSkippableError,
    PromptsResponse,
)
from services.prompt_generators import (
    VisitTypePromptGenerator,
    ConditionPromptGenerator,
    AlertPromptGenerator,
)
from services.encounter_note_service import EncounterContext


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def prompt_repo():
    """Create a fresh prompt repository."""
    return EncounterPromptRepository()


@pytest.fixture
def encounter_repo():
    """Create a fresh encounter repository."""
    repo = EncounterRepository()
    repo._store.clear()
    return repo


@pytest.fixture
def patient_repo():
    """Create a fresh patient repository."""
    repo = PatientRepository()
    repo._store.clear()
    return repo


@pytest.fixture
def alert_repo():
    """Create a fresh alert repository."""
    return ClinicalAlertRepository()


@pytest.fixture
def sample_patient():
    """Create a sample patient with conditions."""
    return Patient(
        id="patient-001",
        name=HumanName(family="Doe", given=["John"]),
        birth_date=datetime(1960, 1, 15).date(),
        problem_list=[
            Problem(
                name="Type 2 Diabetes Mellitus",
                icd10_code="E11.9",
                onset_date=datetime(2020, 1, 15).date(),
                status=ProblemStatus.ACTIVE,
            ),
            Problem(
                name="Essential Hypertension",
                icd10_code="I10",
                onset_date=datetime(2018, 6, 1).date(),
                status=ProblemStatus.ACTIVE,
            ),
        ],
    )


@pytest.fixture
def sample_encounter():
    """Create a sample encounter."""
    return Encounter(
        id="encounter-001",
        status=EncounterStatus.IN_PROGRESS,
        subject=Reference.to("Patient", "patient-001", "John Doe"),
    )


@pytest.fixture
def mock_encounter_note_service(sample_patient):
    """Create a mock encounter note service."""
    service = MagicMock()
    service.patient_repo = MagicMock()
    service.patient_repo.get = AsyncMock(return_value=sample_patient)

    # Create a mock encounter with context
    mock_context = EncounterContext(
        vitals=[],
        medications=[],
        allergies=[],
        problems=[],
        recent_labs=[],
        recent_visits=[],
    )

    mock_encounter_with_context = MagicMock()
    mock_encounter_with_context.encounter = MagicMock()
    mock_encounter_with_context.encounter.patient_id = "patient-001"
    mock_encounter_with_context.context = mock_context

    service.get_encounter_with_context = AsyncMock(return_value=mock_encounter_with_context)

    return service


@pytest.fixture
def service(prompt_repo, encounter_repo, mock_encounter_note_service, patient_repo, alert_repo):
    """Create an encounter prompt service with all generators."""
    return EncounterPromptServiceBuilder.build(
        prompt_repo=prompt_repo,
        encounter_repo=encounter_repo,
        encounter_note_service=mock_encounter_note_service,
        patient_repo=patient_repo,
        alert_repo=alert_repo,
    )


@pytest.mark.unit
class TestVisitTypePromptGenerator:
    """Tests for visit type prompt generator."""

    def test_generates_follow_up_prompts(self, sample_patient):
        """Test generating prompts for follow-up visit."""
        generator = VisitTypePromptGenerator()
        context = EncounterContext()

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=sample_patient,
            context=context,
            visit_type="follow_up",
        ))

        assert len(prompts) >= 5
        assert any(p.prompt_type == "chief_complaint" for p in prompts)
        assert any(p.prompt_type == "review" for p in prompts)
        assert any(p.prompt_type == "assessment" for p in prompts)
        assert any(p.prompt_type == "plan" for p in prompts)

    def test_generates_annual_physical_prompts(self, sample_patient):
        """Test generating prompts for annual physical."""
        generator = VisitTypePromptGenerator()
        context = EncounterContext()

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=sample_patient,
            context=context,
            visit_type="annual_physical",
        ))

        # Annual physical has more prompts
        assert len(prompts) >= 8
        # Should have family/social history prompts
        assert any(p.prompt_subtype == "family_history" for p in prompts)
        assert any(p.prompt_subtype == "social_history" for p in prompts)

    def test_generates_urgent_prompts(self, sample_patient):
        """Test generating prompts for urgent visit."""
        generator = VisitTypePromptGenerator()
        context = EncounterContext()

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=sample_patient,
            context=context,
            visit_type="urgent",
        ))

        # Urgent visit has fewer prompts - focused
        assert len(prompts) <= 6
        assert any(p.prompt_subtype == "acute_complaint" for p in prompts)


@pytest.mark.unit
class TestConditionPromptGenerator:
    """Tests for condition prompt generator."""

    def test_generates_diabetes_prompts(self, patient_repo, sample_patient):
        """Test generating prompts for diabetic patient."""
        patient_repo._store[sample_patient.id] = sample_patient

        generator = ConditionPromptGenerator(patient_repo)
        context = EncounterContext()

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=sample_patient,
            context=context,
            visit_type="follow_up",
        ))

        # Should have A1C review prompt
        assert any(p.prompt_subtype == "a1c_review" for p in prompts)
        # Should have complications screening
        assert any(p.prompt_subtype == "diabetes_complications" for p in prompts)

    def test_generates_hypertension_prompts(self, patient_repo, sample_patient):
        """Test generating prompts for hypertensive patient."""
        patient_repo._store[sample_patient.id] = sample_patient

        generator = ConditionPromptGenerator(patient_repo)
        context = EncounterContext()

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=sample_patient,
            context=context,
            visit_type="follow_up",
        ))

        # Should have BP review prompt
        assert any(p.prompt_subtype == "bp_review" for p in prompts)

    def test_no_prompts_for_healthy_patient(self, patient_repo):
        """Test no condition prompts for patient without conditions."""
        healthy_patient = Patient(
            id="patient-002",
            name=HumanName(family="Doe", given=["Jane"]),
            birth_date=datetime(1990, 1, 15).date(),
            problem_list=[],
        )
        patient_repo._store[healthy_patient.id] = healthy_patient

        generator = ConditionPromptGenerator(patient_repo)
        context = EncounterContext()

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=healthy_patient,
            context=context,
            visit_type="follow_up",
        ))

        assert len(prompts) == 0

    def test_medication_based_prompts(self, patient_repo):
        """Test prompts generated based on medications."""
        patient = Patient(
            id="patient-003",
            name=HumanName(family="Smith", given=["Bob"]),
            birth_date=datetime(1950, 1, 15).date(),
            problem_list=[],  # No conditions but on warfarin
        )
        patient_repo._store[patient.id] = patient

        # Context with warfarin medication
        medication = MagicMock()
        medication.medication_name = "Warfarin 5mg"
        context = EncounterContext(medications=[medication])

        generator = ConditionPromptGenerator(patient_repo)

        prompts = run_async(generator.generate_prompts(
            encounter_id="encounter-001",
            patient=patient,
            context=context,
            visit_type="follow_up",
        ))

        # Should have INR review prompt
        assert any(p.prompt_subtype == "inr_review" for p in prompts)


@pytest.mark.unit
class TestEncounterPromptService:
    """Tests for the encounter prompt service."""

    def test_generate_prompts_creates_prompts(self, service, encounter_repo, sample_encounter):
        """Test that generate_prompts creates prompts in the repository."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        result = run_async(service.generate_prompts(
            encounter_id="encounter-001",
            visit_type="follow_up",
        ))

        assert result.total_count > 0
        assert result.pending_count == result.total_count  # All new prompts are pending

    def test_generate_prompts_clears_existing(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test that generate_prompts clears existing prompts."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        # Add an existing prompt
        existing_prompt = EncounterPrompt(
            id="old-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Old prompt",
            prompt_order=0,
        )
        prompt_repo._store[existing_prompt.id] = existing_prompt

        result = run_async(service.generate_prompts(
            encounter_id="encounter-001",
            visit_type="follow_up",
        ))

        # Old prompt should be gone
        old = run_async(prompt_repo.get("old-prompt"))
        assert old is None

    def test_generate_prompts_includes_condition_prompts(self, service, encounter_repo, sample_encounter):
        """Test that condition-specific prompts are included."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        result = run_async(service.generate_prompts(
            encounter_id="encounter-001",
            visit_type="follow_up",
        ))

        # Should have diabetes prompt for our diabetic patient
        prompts = result.prompts
        assert any(p.prompt_subtype == "a1c_review" for p in prompts)

    def test_generate_prompts_orders_correctly(self, service, encounter_repo, sample_encounter):
        """Test that prompts are ordered by priority."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        result = run_async(service.generate_prompts(
            encounter_id="encounter-001",
            visit_type="follow_up",
        ))

        prompts = result.prompts
        orders = [p.prompt_order for p in prompts]
        assert orders == sorted(orders)  # Should be in ascending order

    def test_generate_prompts_encounter_not_found(self, service):
        """Test error when encounter not found."""
        service.encounter_note_service.get_encounter_with_context = AsyncMock(
            side_effect=Exception("Encounter not found")
        )

        with pytest.raises(EncounterNotFoundError):
            run_async(service.generate_prompts(
                encounter_id="nonexistent",
                visit_type="follow_up",
            ))

    def test_get_encounter_prompts(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test getting prompts for an encounter."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        # Add some prompts
        prompts = [
            EncounterPrompt(
                id="prompt-1",
                encounter_id="encounter-001",
                prompt_type="review",
                prompt_text="First prompt",
                prompt_order=0,
                status="pending",
            ),
            EncounterPrompt(
                id="prompt-2",
                encounter_id="encounter-001",
                prompt_type="assessment",
                prompt_text="Second prompt",
                prompt_order=1,
                status="addressed",
            ),
        ]
        for p in prompts:
            prompt_repo._store[p.id] = p

        result = run_async(service.get_encounter_prompts("encounter-001"))

        assert result.total_count == 2
        assert result.pending_count == 1
        assert result.addressed_count == 1

    def test_get_encounter_prompts_filters_by_status(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test filtering prompts by status."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        # Add prompts with different statuses
        prompts = [
            EncounterPrompt(
                id="prompt-1",
                encounter_id="encounter-001",
                prompt_type="review",
                prompt_text="Pending",
                prompt_order=0,
                status="pending",
            ),
            EncounterPrompt(
                id="prompt-2",
                encounter_id="encounter-001",
                prompt_type="assessment",
                prompt_text="Addressed",
                prompt_order=1,
                status="addressed",
            ),
        ]
        for p in prompts:
            prompt_repo._store[p.id] = p

        result = run_async(service.get_encounter_prompts(
            "encounter-001",
            status="pending",
        ))

        assert result.total_count == 1
        assert result.prompts[0].status == "pending"

    def test_update_prompt_address(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test addressing a prompt."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        prompt = EncounterPrompt(
            id="prompt-1",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test prompt",
            prompt_order=0,
            status="pending",
        )
        prompt_repo._store[prompt.id] = prompt

        result = run_async(service.update_prompt(
            encounter_id="encounter-001",
            prompt_id="prompt-1",
            action="address",
            user_id="dr-smith",
            response_data={"notes": "Reviewed vitals"},
        ))

        assert result.status == "addressed"
        assert result.addressed_by_id == "dr-smith"
        assert result.response_data == {"notes": "Reviewed vitals"}

    def test_update_prompt_skip(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test skipping a prompt."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        prompt = EncounterPrompt(
            id="prompt-1",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test prompt",
            prompt_order=0,
            status="pending",
            is_skippable=True,
        )
        prompt_repo._store[prompt.id] = prompt

        result = run_async(service.update_prompt(
            encounter_id="encounter-001",
            prompt_id="prompt-1",
            action="skip",
            user_id="dr-smith",
            skip_reason="Not applicable",
        ))

        assert result.status == "skipped"
        assert result.response_data == {"skip_reason": "Not applicable"}

    def test_update_prompt_skip_not_skippable(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test error when trying to skip non-skippable prompt."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        prompt = EncounterPrompt(
            id="prompt-1",
            encounter_id="encounter-001",
            prompt_type="chief_complaint",
            prompt_text="Required prompt",
            prompt_order=0,
            status="pending",
            is_skippable=False,
        )
        prompt_repo._store[prompt.id] = prompt

        with pytest.raises(PromptNotSkippableError):
            run_async(service.update_prompt(
                encounter_id="encounter-001",
                prompt_id="prompt-1",
                action="skip",
                user_id="dr-smith",
            ))

    def test_update_prompt_defer(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test deferring a prompt."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        prompt = EncounterPrompt(
            id="prompt-1",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test prompt",
            prompt_order=0,
            status="pending",
        )
        prompt_repo._store[prompt.id] = prompt

        result = run_async(service.update_prompt(
            encounter_id="encounter-001",
            prompt_id="prompt-1",
            action="defer",
            user_id="dr-smith",
        ))

        assert result.status == "deferred"

    def test_update_prompt_not_found(self, service, encounter_repo, sample_encounter):
        """Test error when prompt not found."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        with pytest.raises(PromptNotFoundError):
            run_async(service.update_prompt(
                encounter_id="encounter-001",
                prompt_id="nonexistent",
                action="address",
                user_id="dr-smith",
            ))

    def test_reorder_prompts(self, service, prompt_repo, encounter_repo, sample_encounter):
        """Test reordering prompts."""
        encounter_repo._store[sample_encounter.id] = sample_encounter

        # Add prompts
        prompts = [
            EncounterPrompt(
                id="prompt-1",
                encounter_id="encounter-001",
                prompt_type="review",
                prompt_text="First",
                prompt_order=0,
            ),
            EncounterPrompt(
                id="prompt-2",
                encounter_id="encounter-001",
                prompt_type="assessment",
                prompt_text="Second",
                prompt_order=1,
            ),
            EncounterPrompt(
                id="prompt-3",
                encounter_id="encounter-001",
                prompt_type="plan",
                prompt_text="Third",
                prompt_order=2,
            ),
        ]
        for p in prompts:
            prompt_repo._store[p.id] = p

        # Reorder: 3, 1, 2
        result = run_async(service.reorder_prompts(
            encounter_id="encounter-001",
            prompt_ids=["prompt-3", "prompt-1", "prompt-2"],
        ))

        assert result[0].id == "prompt-3"
        assert result[0].prompt_order == 0
        assert result[1].id == "prompt-1"
        assert result[1].prompt_order == 1
        assert result[2].id == "prompt-2"
        assert result[2].prompt_order == 2


@pytest.mark.unit
class TestPromptsResponse:
    """Tests for PromptsResponse."""

    def test_to_dict(self):
        """Test serialization of PromptsResponse."""
        prompts = [
            EncounterPrompt(
                id="prompt-1",
                encounter_id="encounter-001",
                prompt_type="review",
                prompt_text="Test prompt",
                prompt_order=0,
            )
        ]

        response = PromptsResponse(
            prompts=prompts,
            total_count=1,
            pending_count=1,
            addressed_count=0,
            critical_count=0,
        )
        result = response.to_dict()

        assert "prompts" in result
        assert "totalCount" in result
        assert "pendingCount" in result
        assert result["totalCount"] == 1


@pytest.mark.unit
class TestServiceBuilder:
    """Tests for EncounterPromptServiceBuilder."""

    def test_builds_with_all_repos(self, prompt_repo, encounter_repo, mock_encounter_note_service, patient_repo, alert_repo):
        """Test building service with all repositories."""
        service = EncounterPromptServiceBuilder.build(
            prompt_repo=prompt_repo,
            encounter_repo=encounter_repo,
            encounter_note_service=mock_encounter_note_service,
            patient_repo=patient_repo,
            alert_repo=alert_repo,
        )

        # Should have 4 generators: visit type, condition, alert, follow-up
        assert len(service.generators) == 4

    def test_builds_with_minimal_repos(self, prompt_repo, encounter_repo, mock_encounter_note_service):
        """Test building service with minimal repositories."""
        service = EncounterPromptServiceBuilder.build(
            prompt_repo=prompt_repo,
            encounter_repo=encounter_repo,
            encounter_note_service=mock_encounter_note_service,
        )

        # Should have 2 generators: visit type, follow-up
        assert len(service.generators) == 2
