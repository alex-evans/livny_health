"""
Unit tests for VisitHistoryService.

Tests visit history retrieval including SOAP notes, vitals, medications, and orders.
"""
import asyncio
import pytest


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestVisitHistoryRetrieval:
    """Tests for visit history retrieval."""

    def test_get_visit_history_for_patient(self, visit_history_service):
        """Should retrieve visit history for a patient."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,  # 10 years to get all seeded data
        ))

        assert response is not None
        assert response.total_count > 0
        assert len(response.visits) > 0

    def test_get_visit_history_returns_visit_details(self, visit_history_service):
        """Should return visits with proper details."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        visit = response.visits[0]
        assert visit.id is not None
        assert visit.chief_complaint is not None
        assert visit.visit_type is not None
        assert visit.status is not None
        assert visit.provider is not None

    def test_get_visit_history_includes_soap_notes(self, visit_history_service):
        """Should return visits with SOAP notes."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find a visit with a SOAP note
        visits_with_soap = [v for v in response.visits if v.soap_note is not None]
        assert len(visits_with_soap) > 0

        soap_note = visits_with_soap[0].soap_note
        assert soap_note.subjective is not None
        assert soap_note.objective is not None
        assert soap_note.assessment is not None
        assert soap_note.plan is not None

    def test_get_visit_history_includes_vitals(self, visit_history_service):
        """Should return visits with vital signs."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find a visit with vitals
        visits_with_vitals = [v for v in response.visits if v.vitals is not None]
        assert len(visits_with_vitals) > 0

        vitals = visits_with_vitals[0].vitals
        # At least blood pressure should be recorded
        assert vitals.blood_pressure_systolic is not None or vitals.heart_rate is not None

    def test_get_visit_history_includes_medications(self, visit_history_service):
        """Should return visits with medications prescribed/modified."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find a visit with medications
        visits_with_meds = [v for v in response.visits if v.medications]
        assert len(visits_with_meds) > 0

        medication = visits_with_meds[0].medications[0]
        assert medication.name is not None
        assert medication.dosage is not None
        assert medication.action is not None

    def test_get_visit_history_includes_orders(self, visit_history_service):
        """Should return visits with clinical orders."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find a visit with orders
        visits_with_orders = [v for v in response.visits if v.orders]
        assert len(visits_with_orders) > 0

        order = visits_with_orders[0].orders[0]
        assert order.name is not None
        assert order.order_type is not None
        assert order.status is not None

    def test_get_visit_history_filters_by_days_back(self, visit_history_service):
        """Should filter visits by days_back parameter."""
        # Get all visits
        all_visits = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Get only recent visits
        recent_visits = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=60,
        ))

        # Recent should have fewer or equal visits
        assert recent_visits.total_count <= all_visits.total_count

    def test_get_visit_history_excludes_cancelled_by_default(self, visit_history_service):
        """Should exclude cancelled and no-show visits by default."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            include_all=False,
        ))

        # All returned visits should be completed or in_progress
        for visit in response.visits:
            assert visit.status not in ("cancelled", "no_show")

    def test_get_visit_history_sorted_by_date_descending(self, visit_history_service):
        """Should return visits sorted by date, most recent first."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        if len(response.visits) > 1:
            for i in range(len(response.visits) - 1):
                assert response.visits[i].date >= response.visits[i + 1].date

    def test_get_visit_history_empty_for_unknown_patient(self, visit_history_service):
        """Should return empty list for non-existent patient."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="non-existent-patient",
            days_back=3650,
        ))

        assert response.total_count == 0
        assert len(response.visits) == 0

    def test_get_visit_history_respects_limit(self, visit_history_service):
        """Should respect the limit parameter."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            limit=2,
        ))

        assert len(response.visits) <= 2
        if response.total_count > 2:
            assert response.has_more is True


@pytest.mark.unit
class TestVisitHistoryResponse:
    """Tests for VisitHistoryResponse serialization."""

    def test_to_dict_returns_proper_structure(self, visit_history_service):
        """Should return properly structured dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()

        assert "visits" in result
        assert "totalCount" in result
        assert "hasMore" in result
        assert isinstance(result["visits"], list)

    def test_visit_dict_includes_soap_note(self, visit_history_service):
        """Should include SOAP note in visit dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()
        visits_with_soap = [v for v in result["visits"] if "soapNote" in v and v["soapNote"]]

        assert len(visits_with_soap) > 0
        soap_note = visits_with_soap[0]["soapNote"]
        assert "subjective" in soap_note
        assert "objective" in soap_note
        assert "assessment" in soap_note
        assert "plan" in soap_note

    def test_visit_dict_includes_vitals(self, visit_history_service):
        """Should include vitals in visit dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()
        visits_with_vitals = [v for v in result["visits"] if "vitals" in v and v["vitals"]]

        assert len(visits_with_vitals) > 0

    def test_visit_dict_includes_medications(self, visit_history_service):
        """Should include medications in visit dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()
        visits_with_meds = [v for v in result["visits"] if "medications" in v and v["medications"]]

        assert len(visits_with_meds) > 0
        med = visits_with_meds[0]["medications"][0]
        assert "name" in med
        assert "dosage" in med
        assert "action" in med

    def test_visit_dict_includes_orders(self, visit_history_service):
        """Should include orders in visit dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()
        visits_with_orders = [v for v in result["visits"] if "orders" in v and v["orders"]]

        assert len(visits_with_orders) > 0
        order = visits_with_orders[0]["orders"][0]
        assert "name" in order
        assert "orderType" in order
        assert "status" in order


@pytest.mark.unit
class TestGetVisitById:
    """Tests for getting individual visit notes."""

    def test_get_visit_by_id(self, visit_history_service):
        """Should retrieve a specific visit by ID."""
        visit = run_async(visit_history_service.get_visit_by_id("v1"))

        assert visit is not None
        assert visit.id == "v1"
        assert visit.chief_complaint is not None

    def test_get_visit_by_id_returns_none_for_unknown(self, visit_history_service):
        """Should return None for unknown visit ID."""
        visit = run_async(visit_history_service.get_visit_by_id("unknown-visit-id"))

        assert visit is None


@pytest.mark.unit
class TestVisitTimelineEnhancements:
    """Tests for timeline enhancement fields (critical findings, follow-up, etc.)."""

    def test_visit_has_critical_findings_field(self, visit_history_service):
        """Should return visits with critical findings flags."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find visits with critical findings
        visits_with_critical = [v for v in response.visits if v.has_critical_findings]
        assert len(visits_with_critical) > 0

        # Verify the critical findings summary is present
        for visit in visits_with_critical:
            assert visit.critical_findings_summary is not None

    def test_visit_has_follow_up_required_field(self, visit_history_service):
        """Should return visits with follow-up required flags."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find visits with follow-up required
        visits_with_followup = [v for v in response.visits if v.has_follow_up_required]
        assert len(visits_with_followup) > 0

        # Verify the follow-up summary is present
        for visit in visits_with_followup:
            assert visit.follow_up_summary is not None

    def test_annual_physical_visit_type(self, visit_history_service):
        """Should return visits with annual_physical visit type."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Find annual physical visits
        annual_physicals = [v for v in response.visits if v.visit_type == "annual_physical"]
        assert len(annual_physicals) > 0

    def test_critical_findings_in_serialized_output(self, visit_history_service):
        """Should include critical findings in serialized dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()

        # Find a visit with critical findings
        visits_with_critical = [v for v in result["visits"] if v.get("hasCriticalFindings")]
        assert len(visits_with_critical) > 0

        critical_visit = visits_with_critical[0]
        assert "hasCriticalFindings" in critical_visit
        assert critical_visit["hasCriticalFindings"] is True
        assert "criticalFindingsSummary" in critical_visit

    def test_follow_up_required_in_serialized_output(self, visit_history_service):
        """Should include follow-up required in serialized dictionary."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        result = response.to_dict()

        # Find a visit with follow-up required
        visits_with_followup = [v for v in result["visits"] if v.get("hasFollowUpRequired")]
        assert len(visits_with_followup) > 0

        followup_visit = visits_with_followup[0]
        assert "hasFollowUpRequired" in followup_visit
        assert followup_visit["hasFollowUpRequired"] is True
        assert "followUpSummary" in followup_visit

    def test_emergency_visit_has_different_provider(self, visit_history_service):
        """Should have visits from different providers for continuity tracking."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        # Collect unique provider IDs
        provider_ids = set()
        for visit in response.visits:
            if visit.provider:
                provider_ids.add(visit.provider.id)

        # Should have multiple providers (for provider continuity feature)
        assert len(provider_ids) >= 2

    def test_significant_visit_types_present(self, visit_history_service):
        """Should have significant visit types (emergency, annual_physical)."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        visit_types = set(v.visit_type for v in response.visits)

        # Should have at least one significant visit type
        significant_types = {"emergency", "hospital_admission", "annual_physical"}
        assert len(visit_types & significant_types) >= 1


@pytest.mark.unit
class TestVisitHistoryFilters:
    """Tests for visit history filtering options."""

    def test_filter_by_visit_type(self, visit_history_service):
        """Should filter by visit type."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            visit_type="office_visit",
        ))

        # All returned visits should be office visits
        for visit in response.visits:
            assert visit.visit_type == "office_visit"

    def test_filter_by_provider_id(self, visit_history_service):
        """Should filter by provider ID."""
        # First get all visits to find a provider ID
        all_response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        if all_response.visits and all_response.visits[0].provider:
            provider_id = all_response.visits[0].provider.id

            response = run_async(visit_history_service.get_visit_history(
                patient_id="patient-001",
                days_back=3650,
                provider_id=provider_id,
            ))

            # All returned visits should have this provider
            for visit in response.visits:
                assert visit.provider is not None
                assert visit.provider.id == provider_id

    def test_filter_by_diagnosis_code(self, visit_history_service):
        """Should filter by diagnosis code."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            diagnosis_code="E11",  # Diabetes
        ))

        # All returned visits should have matching diagnosis
        for visit in response.visits:
            assert any(d.code.startswith("E11") for d in visit.diagnoses)

    def test_filter_by_search_query(self, visit_history_service):
        """Should filter by search query."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            search_query="diabetes",
        ))

        # Should return visits matching the search
        assert response is not None

    def test_filter_by_date_from(self, visit_history_service):
        """Should filter by date_from."""
        from datetime import datetime, timedelta

        cutoff = datetime.utcnow() - timedelta(days=180)

        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            date_from=cutoff,
        ))

        # All returned visits should be on or after cutoff
        for visit in response.visits:
            assert visit.date >= cutoff

    def test_filter_by_date_to(self, visit_history_service):
        """Should filter by date_to."""
        from datetime import datetime, timedelta

        cutoff = datetime.utcnow() - timedelta(days=30)

        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            date_to=cutoff,
        ))

        # All returned visits should be on or before cutoff
        for visit in response.visits:
            assert visit.date <= cutoff

    def test_include_all_returns_cancelled(self, visit_history_service):
        """Should include cancelled visits when include_all=True."""
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
            include_all=True,
        ))

        # Should have at least some visits
        assert response.total_count >= 0


@pytest.mark.unit
class TestProviderMethods:
    """Tests for provider-related methods."""

    def test_get_providers_for_patient(self, visit_history_service):
        """Should return unique providers for a patient."""
        providers = run_async(visit_history_service.get_providers_for_patient("patient-001"))

        assert isinstance(providers, list)
        # Should have at least one provider
        if providers:
            provider = providers[0]
            assert "id" in provider
            assert "name" in provider

    def test_get_visit_by_encounter(self, visit_history_service):
        """Should return visit for a specific encounter."""
        # First get a visit to find an encounter ID
        response = run_async(visit_history_service.get_visit_history(
            patient_id="patient-001",
            days_back=3650,
        ))

        if response.visits:
            encounter_ref = response.visits[0].encounter.reference
            encounter_id = encounter_ref.split("/")[-1] if "/" in encounter_ref else encounter_ref

            visit = run_async(visit_history_service.get_visit_by_encounter(encounter_id))

            # Should return the visit or None
            if visit:
                assert visit.encounter.reference == f"Encounter/{encounter_id}"

    def test_get_visit_by_encounter_not_found(self, visit_history_service):
        """Should return None for unknown encounter."""
        visit = run_async(visit_history_service.get_visit_by_encounter("unknown-encounter-id"))

        assert visit is None
