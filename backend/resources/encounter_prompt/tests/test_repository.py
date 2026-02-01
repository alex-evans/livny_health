"""Tests for encounter prompt repository."""

import asyncio
import pytest
from datetime import datetime

from resources.encounter_prompt import (
    EncounterPrompt,
    EncounterPromptRepository,
)


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def repo():
    """Create a fresh repository."""
    return EncounterPromptRepository()


@pytest.fixture
def sample_prompts():
    """Create sample prompts for testing."""
    return [
        EncounterPrompt(
            id="prompt-1",
            encounter_id="encounter-001",
            prompt_type="chief_complaint",
            prompt_subtype="reason_for_visit",
            prompt_text="What brings the patient in today?",
            prompt_order=0,
            status="pending",
            viewer_section="subjective",
            is_skippable=False,
        ),
        EncounterPrompt(
            id="prompt-2",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_subtype="vitals",
            prompt_text="Review vital signs",
            prompt_order=1,
            status="pending",
            viewer_section="objective",
            is_skippable=True,
        ),
        EncounterPrompt(
            id="prompt-3",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_subtype="a1c_review",
            prompt_text="Review A1C",
            prompt_order=2,
            status="addressed",
            viewer_section="objective",
            is_skippable=True,
        ),
        EncounterPrompt(
            id="prompt-4",
            encounter_id="encounter-002",  # Different encounter
            prompt_type="review",
            prompt_text="Other encounter prompt",
            prompt_order=0,
            status="pending",
        ),
    ]


@pytest.mark.unit
class TestEncounterPromptRepository:
    """Tests for EncounterPromptRepository."""

    def test_create_and_get(self, repo):
        """Test creating and retrieving a prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test prompt",
            prompt_order=0,
        )

        run_async(repo.create(prompt))
        result = run_async(repo.get("test-prompt"))

        assert result is not None
        assert result.id == "test-prompt"
        assert result.prompt_text == "Test prompt"

    def test_get_not_found(self, repo):
        """Test getting a non-existent prompt."""
        result = run_async(repo.get("nonexistent"))
        assert result is None

    def test_update(self, repo):
        """Test updating a prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test prompt",
            prompt_order=0,
            status="pending",
        )

        run_async(repo.create(prompt))

        # Update the prompt
        prompt.status = "addressed"
        prompt.addressed_at = datetime.utcnow()
        prompt.addressed_by_id = "dr-smith"

        run_async(repo.update("test-prompt", prompt))
        result = run_async(repo.get("test-prompt"))

        assert result.status == "addressed"
        assert result.addressed_by_id == "dr-smith"

    def test_delete(self, repo):
        """Test deleting a prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test prompt",
            prompt_order=0,
        )

        run_async(repo.create(prompt))
        deleted = run_async(repo.delete("test-prompt"))

        assert deleted is True
        assert run_async(repo.get("test-prompt")) is None

    def test_delete_not_found(self, repo):
        """Test deleting a non-existent prompt."""
        deleted = run_async(repo.delete("nonexistent"))
        assert deleted is False

    def test_list_filters_by_encounter_id(self, repo, sample_prompts):
        """Test filtering by encounter_id."""
        for p in sample_prompts:
            run_async(repo.create(p))

        results = run_async(repo.list(encounter_id="encounter-001"))

        assert len(results) == 3
        assert all(r.encounter_id == "encounter-001" for r in results)

    def test_list_filters_by_status(self, repo, sample_prompts):
        """Test filtering by status."""
        for p in sample_prompts:
            run_async(repo.create(p))

        results = run_async(repo.list(
            encounter_id="encounter-001",
            status="pending",
        ))

        assert len(results) == 2
        assert all(r.status == "pending" for r in results)

    def test_list_filters_by_multiple_statuses(self, repo, sample_prompts):
        """Test filtering by multiple statuses."""
        for p in sample_prompts:
            run_async(repo.create(p))

        results = run_async(repo.list(
            encounter_id="encounter-001",
            status=["pending", "addressed"],
        ))

        assert len(results) == 3

    def test_list_filters_by_prompt_type(self, repo, sample_prompts):
        """Test filtering by prompt_type."""
        for p in sample_prompts:
            run_async(repo.create(p))

        results = run_async(repo.list(
            encounter_id="encounter-001",
            prompt_type="review",
        ))

        assert len(results) == 2
        assert all(r.prompt_type == "review" for r in results)

    def test_list_filters_by_viewer_section(self, repo, sample_prompts):
        """Test filtering by viewer_section."""
        for p in sample_prompts:
            run_async(repo.create(p))

        results = run_async(repo.list(
            encounter_id="encounter-001",
            viewer_section="objective",
        ))

        assert len(results) == 2
        assert all(r.viewer_section == "objective" for r in results)

    def test_get_by_encounter_sorted_by_order(self, repo, sample_prompts):
        """Test that get_by_encounter returns sorted results."""
        # Add in random order
        for p in [sample_prompts[2], sample_prompts[0], sample_prompts[1]]:
            run_async(repo.create(p))

        results = run_async(repo.get_by_encounter("encounter-001"))

        orders = [r.prompt_order for r in results]
        assert orders == sorted(orders)

    def test_get_by_encounter_with_status_filter(self, repo, sample_prompts):
        """Test get_by_encounter with status filter."""
        for p in sample_prompts:
            run_async(repo.create(p))

        results = run_async(repo.get_by_encounter(
            "encounter-001",
            status="addressed",
        ))

        assert len(results) == 1
        assert results[0].status == "addressed"

    def test_clear_encounter_prompts(self, repo, sample_prompts):
        """Test clearing all prompts for an encounter."""
        for p in sample_prompts:
            run_async(repo.create(p))

        count = run_async(repo.clear_encounter_prompts("encounter-001"))

        assert count == 3

        # Verify they're gone
        results = run_async(repo.get_by_encounter("encounter-001"))
        assert len(results) == 0

        # Other encounter should be unaffected
        results = run_async(repo.get_by_encounter("encounter-002"))
        assert len(results) == 1

    def test_bulk_create(self, repo):
        """Test creating multiple prompts at once."""
        prompts = [
            EncounterPrompt(
                id=f"prompt-{i}",
                encounter_id="encounter-001",
                prompt_type="review",
                prompt_text=f"Prompt {i}",
                prompt_order=i,
            )
            for i in range(5)
        ]

        created = run_async(repo.bulk_create(prompts))

        assert len(created) == 5

        # Verify all exist
        for i in range(5):
            result = run_async(repo.get(f"prompt-{i}"))
            assert result is not None

    def test_update_prompt_orders(self, repo, sample_prompts):
        """Test reordering prompts."""
        for p in sample_prompts[:3]:
            run_async(repo.create(p))

        # Reorder: prompt-3, prompt-1, prompt-2
        updated = run_async(repo.update_prompt_orders(
            "encounter-001",
            ["prompt-3", "prompt-1", "prompt-2"],
        ))

        assert len(updated) == 3
        assert updated[0].id == "prompt-3"
        assert updated[0].prompt_order == 0
        assert updated[1].id == "prompt-1"
        assert updated[1].prompt_order == 1
        assert updated[2].id == "prompt-2"
        assert updated[2].prompt_order == 2

    def test_update_prompt_orders_ignores_wrong_encounter(self, repo, sample_prompts):
        """Test that reorder ignores prompts from other encounters."""
        for p in sample_prompts:
            run_async(repo.create(p))

        # Try to include prompt from different encounter
        updated = run_async(repo.update_prompt_orders(
            "encounter-001",
            ["prompt-4", "prompt-1", "prompt-2"],  # prompt-4 is from encounter-002
        ))

        # Should only update prompts from encounter-001
        assert len(updated) == 2


@pytest.mark.unit
class TestEncounterPromptModel:
    """Tests for EncounterPrompt model methods."""

    def test_address(self):
        """Test addressing a prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test",
            prompt_order=0,
            status="pending",
        )

        prompt.address(by_id="dr-smith", response={"notes": "Done"})

        assert prompt.status == "addressed"
        assert prompt.addressed_by_id == "dr-smith"
        assert prompt.addressed_at is not None
        assert prompt.response_data == {"notes": "Done"}

    def test_skip(self):
        """Test skipping a prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test",
            prompt_order=0,
            status="pending",
            is_skippable=True,
        )

        prompt.skip(by_id="dr-smith", reason="Not applicable")

        assert prompt.status == "skipped"
        assert prompt.addressed_by_id == "dr-smith"
        assert prompt.response_data == {"skip_reason": "Not applicable"}

    def test_skip_not_skippable_raises(self):
        """Test that skip raises for non-skippable prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="chief_complaint",
            prompt_text="Required",
            prompt_order=0,
            status="pending",
            is_skippable=False,
        )

        with pytest.raises(ValueError, match="cannot be skipped"):
            prompt.skip(by_id="dr-smith")

    def test_defer(self):
        """Test deferring a prompt."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_text="Test",
            prompt_order=0,
            status="pending",
        )

        prompt.defer(by_id="dr-smith")

        assert prompt.status == "deferred"
        assert prompt.addressed_by_id == "dr-smith"
        assert prompt.addressed_at is not None

    def test_to_dict(self):
        """Test serialization to dictionary."""
        prompt = EncounterPrompt(
            id="test-prompt",
            encounter_id="encounter-001",
            prompt_type="review",
            prompt_subtype="vitals",
            prompt_text="Review vitals",
            prompt_order=0,
            status="pending",
            viewer_section="objective",
            is_skippable=True,
        )

        result = prompt.to_dict()

        assert result["id"] == "test-prompt"
        assert result["encounterId"] == "encounter-001"
        assert result["promptType"] == "review"
        assert result["promptSubtype"] == "vitals"
        assert result["promptText"] == "Review vitals"
        assert result["promptOrder"] == 0
        assert result["status"] == "pending"
        assert result["viewerSection"] == "objective"
        assert result["isSkippable"] is True
