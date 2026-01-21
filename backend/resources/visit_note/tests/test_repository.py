"""
Unit tests for VisitNoteRepository.
"""
import asyncio
import pytest
from datetime import datetime, timedelta

from resources.visit_note import (
    VisitNote,
    VisitNoteRepository,
    SOAPNote,
    VisitDiagnosis,
    VisitProvider,
)
from resources.core import Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestVisitNoteRepository:
    """Tests for VisitNoteRepository."""

    @pytest.fixture
    def repo(self):
        """Create a repository."""
        return VisitNoteRepository()

    @pytest.fixture
    def test_visit_notes(self, repo):
        """Create test visit notes."""
        now = datetime.utcnow()
        notes = [
            # Recent completed visit for patient-001
            VisitNote(
                id="note-001",
                encounter=Reference(reference="Encounter/enc-001"),
                subject=Reference(reference="Patient/patient-001"),
                visit_type="office_visit",
                status="completed",
                date=now - timedelta(days=5),
                chief_complaint="Headache and fatigue",
                provider=VisitProvider(id="pract-001", name="Dr. Smith", role="Attending", specialty="Internal Medicine"),
                soap_note=SOAPNote(
                    subjective="Patient reports headache for 3 days",
                    objective="BP 120/80, temp normal",
                    assessment="Tension headache",
                    plan="OTC pain relief, rest",
                ),
                diagnoses=[
                    VisitDiagnosis(code="G44.1", description="Tension headache", is_primary=True),
                ],
            ),
            # Older visit for patient-001
            VisitNote(
                id="note-002",
                encounter=Reference(reference="Encounter/enc-002"),
                subject=Reference(reference="Patient/patient-001"),
                visit_type="follow_up",
                status="completed",
                date=now - timedelta(days=60),
                chief_complaint="Diabetes follow-up",
                provider=VisitProvider(id="pract-002", name="Dr. Jones", role="Attending"),
                diagnoses=[
                    VisitDiagnosis(code="E11.9", description="Type 2 diabetes", is_primary=True),
                ],
            ),
            # Visit for patient-002
            VisitNote(
                id="note-003",
                encounter=Reference(reference="Encounter/enc-003"),
                subject=Reference(reference="Patient/patient-002"),
                visit_type="telehealth",
                status="completed",
                date=now - timedelta(days=10),
                chief_complaint="Cough and cold",
                provider=VisitProvider(id="pract-001", name="Dr. Smith", role="Attending"),
                soap_note=SOAPNote(
                    subjective="Cough for 1 week",
                    objective="Lungs clear",
                    assessment="Viral URI",
                    plan="Rest and fluids",
                ),
                notes="Patient to follow up if symptoms worsen",
            ),
            # Cancelled visit
            VisitNote(
                id="note-004",
                encounter=Reference(reference="Encounter/enc-004"),
                subject=Reference(reference="Patient/patient-001"),
                visit_type="office_visit",
                status="cancelled",
                date=now - timedelta(days=2),
                chief_complaint="Annual checkup",
            ),
            # No-show visit
            VisitNote(
                id="note-005",
                encounter=Reference(reference="Encounter/enc-005"),
                subject=Reference(reference="Patient/patient-001"),
                visit_type="office_visit",
                status="no_show",
                date=now - timedelta(days=15),
                chief_complaint="Flu symptoms",
            ),
        ]
        for n in notes:
            repo._store[n.id] = n
        return notes

    def test_list_all(self, repo, test_visit_notes):
        """list with no filters returns all notes sorted by date desc."""
        result = run_async(repo.list())
        assert len(result) == 5
        # Should be sorted by date descending
        dates = [n.date for n in result]
        assert dates == sorted(dates, reverse=True)

    def test_list_filter_by_patient_id(self, repo, test_visit_notes):
        """list filters by patient ID."""
        result = run_async(repo.list(patient_id="patient-001"))
        assert len(result) == 4
        assert all("patient-001" in n.subject.reference for n in result)

    def test_list_filter_by_encounter_id(self, repo, test_visit_notes):
        """list filters by encounter ID."""
        result = run_async(repo.list(encounter_id="enc-001"))
        assert len(result) == 1
        assert result[0].id == "note-001"

    def test_list_filter_by_status_string(self, repo, test_visit_notes):
        """list filters by single status."""
        result = run_async(repo.list(status="cancelled"))
        assert len(result) == 1
        assert result[0].id == "note-004"

    def test_list_filter_by_status_list(self, repo, test_visit_notes):
        """list filters by multiple statuses."""
        result = run_async(repo.list(status=["cancelled", "no_show"]))
        assert len(result) == 2
        ids = {n.id for n in result}
        assert ids == {"note-004", "note-005"}

    def test_list_filter_by_visit_type_string(self, repo, test_visit_notes):
        """list filters by single visit type."""
        result = run_async(repo.list(visit_type="telehealth"))
        assert len(result) == 1
        assert result[0].id == "note-003"

    def test_list_filter_by_visit_type_list(self, repo, test_visit_notes):
        """list filters by multiple visit types."""
        result = run_async(repo.list(visit_type=["office_visit", "follow_up"]))
        assert len(result) == 4

    def test_list_filter_by_days_back(self, repo, test_visit_notes):
        """list filters by days back."""
        result = run_async(repo.list(days_back=30))
        # Should include notes from last 30 days
        assert all(n.date >= datetime.utcnow() - timedelta(days=30) for n in result)

    def test_list_filter_by_provider_id(self, repo, test_visit_notes):
        """list filters by provider ID."""
        result = run_async(repo.list(provider_id="pract-001"))
        assert len(result) == 2
        ids = {n.id for n in result}
        assert ids == {"note-001", "note-003"}

    def test_list_filter_by_diagnosis_code(self, repo, test_visit_notes):
        """list filters by diagnosis code partial match."""
        result = run_async(repo.list(diagnosis_code="E11"))
        assert len(result) == 1
        assert result[0].id == "note-002"

    def test_list_filter_by_diagnosis_code_case_insensitive(self, repo, test_visit_notes):
        """list diagnosis code filter works with lowercase."""
        result = run_async(repo.list(diagnosis_code="g44"))
        assert len(result) == 1
        assert result[0].id == "note-001"

    def test_list_filter_by_date_from(self, repo, test_visit_notes):
        """list filters by date_from."""
        cutoff = datetime.utcnow() - timedelta(days=10)
        result = run_async(repo.list(date_from=cutoff))
        assert all(n.date >= cutoff for n in result)

    def test_list_filter_by_date_to(self, repo, test_visit_notes):
        """list filters by date_to."""
        cutoff = datetime.utcnow() - timedelta(days=10)
        result = run_async(repo.list(date_to=cutoff))
        assert all(n.date <= cutoff for n in result)

    def test_list_filter_by_search_query_chief_complaint(self, repo, test_visit_notes):
        """list search_query matches chief complaint."""
        result = run_async(repo.list(search_query="headache"))
        assert len(result) == 1
        assert result[0].id == "note-001"

    def test_list_filter_by_search_query_diagnosis(self, repo, test_visit_notes):
        """list search_query matches diagnosis description."""
        result = run_async(repo.list(search_query="diabetes"))
        assert len(result) == 1
        assert result[0].id == "note-002"

    def test_list_filter_by_search_query_soap_note(self, repo, test_visit_notes):
        """list search_query matches SOAP note content."""
        result = run_async(repo.list(search_query="tension"))
        assert len(result) == 1
        assert result[0].id == "note-001"

    def test_list_filter_by_search_query_notes(self, repo, test_visit_notes):
        """list search_query matches notes field."""
        result = run_async(repo.list(search_query="worsen"))
        assert len(result) == 1
        assert result[0].id == "note-003"

    def test_list_multiple_filters(self, repo, test_visit_notes):
        """list with multiple filters applies all."""
        result = run_async(repo.list(patient_id="patient-001", status="completed"))
        assert len(result) == 2
        ids = {n.id for n in result}
        assert ids == {"note-001", "note-002"}

    def test_get_by_patient_excludes_cancelled_by_default(self, repo, test_visit_notes):
        """get_by_patient excludes cancelled and no_show by default."""
        result = run_async(repo.get_by_patient("patient-001"))
        assert len(result) == 2
        statuses = {n.status for n in result}
        assert "cancelled" not in statuses
        assert "no_show" not in statuses

    def test_get_by_patient_with_include_all(self, repo, test_visit_notes):
        """get_by_patient with include_all returns all statuses."""
        result = run_async(repo.get_by_patient("patient-001", include_all=True))
        assert len(result) == 4

    def test_get_by_patient_with_days_back(self, repo, test_visit_notes):
        """get_by_patient with days_back limits results."""
        result = run_async(repo.get_by_patient("patient-001", days_back=30))
        # Should only include recent completed visits
        assert all(n.date >= datetime.utcnow() - timedelta(days=30) for n in result)

    def test_get_by_patient_empty(self, repo, test_visit_notes):
        """get_by_patient returns empty list for unknown patient."""
        result = run_async(repo.get_by_patient("patient-999"))
        assert result == []

    def test_get_by_encounter_found(self, repo, test_visit_notes):
        """get_by_encounter returns note when found."""
        result = run_async(repo.get_by_encounter("enc-001"))
        assert result is not None
        assert result.id == "note-001"

    def test_get_by_encounter_not_found(self, repo, test_visit_notes):
        """get_by_encounter returns None when not found."""
        result = run_async(repo.get_by_encounter("enc-999"))
        assert result is None

    def test_get_unique_providers(self, repo, test_visit_notes):
        """get_unique_providers returns unique providers for patient."""
        result = run_async(repo.get_unique_providers("patient-001"))
        assert len(result) == 2
        provider_ids = {p["id"] for p in result}
        assert provider_ids == {"pract-001", "pract-002"}

    def test_get_unique_providers_empty(self, repo, test_visit_notes):
        """get_unique_providers returns empty list for unknown patient."""
        result = run_async(repo.get_unique_providers("patient-999"))
        assert result == []

    def test_get_by_id(self, repo, test_visit_notes):
        """get returns visit note by ID."""
        result = run_async(repo.get("note-001"))
        assert result is not None
        assert result.chief_complaint == "Headache and fatigue"

    def test_get_by_id_not_found(self, repo, test_visit_notes):
        """get returns None when ID doesn't exist."""
        result = run_async(repo.get("nonexistent"))
        assert result is None

    def test_create(self, repo):
        """create adds a new visit note."""
        new_note = VisitNote(
            id="note-new",
            encounter=Reference(reference="Encounter/enc-new"),
            subject=Reference(reference="Patient/patient-new"),
            chief_complaint="New visit",
        )
        result = run_async(repo.create(new_note))
        assert result.id == "note-new"

        stored = run_async(repo.get("note-new"))
        assert stored is not None

    def test_update(self, repo, test_visit_notes):
        """update modifies an existing visit note."""
        updated = VisitNote(
            id="note-001",
            encounter=Reference(reference="Encounter/enc-001"),
            subject=Reference(reference="Patient/patient-001"),
            status="amended",
            chief_complaint="Updated complaint",
        )
        result = run_async(repo.update("note-001", updated))
        assert result is not None
        assert result.status == "amended"
        assert result.chief_complaint == "Updated complaint"

    def test_delete(self, repo, test_visit_notes):
        """delete removes a visit note."""
        result = run_async(repo.delete("note-001"))
        assert result is True

        stored = run_async(repo.get("note-001"))
        assert stored is None


class TestMatchesSearch:
    """Tests for the _matches_search helper method."""

    @pytest.fixture
    def repo(self):
        return VisitNoteRepository()

    def test_matches_chief_complaint(self, repo):
        """_matches_search matches chief complaint."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Severe headache",
            diagnoses=[],
        )
        assert repo._matches_search(visit, "headache") is True
        assert repo._matches_search(visit, "cough") is False

    def test_matches_diagnosis_code(self, repo):
        """_matches_search matches diagnosis code."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Pain",
            diagnoses=[VisitDiagnosis(code="J06.9", description="Upper respiratory infection")],
        )
        assert repo._matches_search(visit, "j06") is True

    def test_matches_diagnosis_description(self, repo):
        """_matches_search matches diagnosis description."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Symptoms",
            diagnoses=[VisitDiagnosis(code="J06.9", description="Upper respiratory infection")],
        )
        assert repo._matches_search(visit, "respiratory") is True

    def test_matches_soap_subjective(self, repo):
        """_matches_search matches SOAP subjective."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Check",
            diagnoses=[],
            soap_note=SOAPNote(
                subjective="Patient reports dizziness",
                objective="Normal exam",
                assessment="Benign",
                plan="Follow up",
            ),
        )
        assert repo._matches_search(visit, "dizziness") is True

    def test_matches_soap_objective(self, repo):
        """_matches_search matches SOAP objective."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Check",
            diagnoses=[],
            soap_note=SOAPNote(
                subjective="Symptoms",
                objective="Elevated blood pressure noted",
                assessment="HTN",
                plan="Medication",
            ),
        )
        assert repo._matches_search(visit, "elevated") is True

    def test_matches_soap_assessment(self, repo):
        """_matches_search matches SOAP assessment."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Check",
            diagnoses=[],
            soap_note=SOAPNote(
                subjective="Symptoms",
                objective="Exam",
                assessment="Suspected pneumonia",
                plan="X-ray",
            ),
        )
        assert repo._matches_search(visit, "pneumonia") is True

    def test_matches_soap_plan(self, repo):
        """_matches_search matches SOAP plan."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Check",
            diagnoses=[],
            soap_note=SOAPNote(
                subjective="Symptoms",
                objective="Exam",
                assessment="Diagnosis",
                plan="Start antibiotics immediately",
            ),
        )
        assert repo._matches_search(visit, "antibiotics") is True

    def test_matches_notes_field(self, repo):
        """_matches_search matches notes field."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Check",
            diagnoses=[],
            notes="Patient should return in 2 weeks for recheck",
        )
        assert repo._matches_search(visit, "recheck") is True

    def test_no_match_returns_false(self, repo):
        """_matches_search returns False when no match."""
        visit = VisitNote(
            id="v1",
            encounter=Reference(reference="Encounter/e1"),
            subject=Reference(reference="Patient/p1"),
            chief_complaint="Headache",
            diagnoses=[],
        )
        assert repo._matches_search(visit, "xyz123nonexistent") is False
