"""Tests for social family history BFF endpoints."""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from main import app
from bff import dependencies
from resources.social_family_history import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    FamilyMember,
    FamilyMemberCondition,
    SocialFamilyHistoryRepository,
)
from resources.core import Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Ensure data is seeded before running tests
dependencies.ensure_data_seeded()


def create_seeded_sfh_repo():
    """Create a repository with sample social/family history data."""
    repo = SocialFamilyHistoryRepository()

    # Patient-001 history
    history_001 = SocialFamilyHistory(
        id="sfh-001",
        subject=Reference.to("Patient", "patient-001", "Sarah Johnson"),
        social_history=SocialHistory(
            smoking=SmokingHistory(status="former", pack_years=8.5),
            alcohol=AlcoholHistory(use_level="occasional", drinks_per_week=2),
            occupation="Marketing Manager",
            marital_status="married",
            exercise="light",
            last_reviewed=datetime(2025, 1, 15),
            reviewed_by="Dr. Elizabeth Frost",
        ),
        family_history=FamilyHistory(
            family_members=[
                FamilyMember(
                    id="fm-1",
                    relative_type="father",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Type 2 diabetes",
                            icd10_code="E11",
                        ),
                    ],
                ),
            ],
            adoption_status="not_adopted",
        ),
    )

    repo._store["sfh-001"] = history_001

    return repo


@pytest.mark.integration
class TestGetPatientSocialFamilyHistory:
    """Tests for GET /patients/{patient_id}/social-family-history endpoint."""

    def test_get_social_family_history_success(self):
        """Test successfully getting patient social/family history."""
        seeded_repo = create_seeded_sfh_repo()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=seeded_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: seeded_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/social-family-history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert "socialHistory" in data
            assert "familyHistory" in data
            assert "riskAssessments" in data
            assert "hasHighRisk" in data
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service

    def test_get_social_family_history_includes_risk_by_default(self):
        """Test that risk assessments are included by default."""
        seeded_repo = create_seeded_sfh_repo()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=seeded_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: seeded_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/social-family-history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert len(data["riskAssessments"]) > 0
            risk_types = {ra["riskType"] for ra in data["riskAssessments"]}
            assert "cardiovascular" in risk_types
            assert "cancer" in risk_types
            assert "diabetes" in risk_types
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service

    def test_get_social_family_history_without_risk(self):
        """Test excluding risk assessments."""
        seeded_repo = create_seeded_sfh_repo()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=seeded_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: seeded_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get(
                        "/patients/patient-001/social-family-history?include_risk_assessments=false"
                    )

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert data["riskAssessments"] == []
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service

    def test_get_social_family_history_patient_not_found(self):
        """Test 404 for unknown patient."""
        seeded_repo = create_seeded_sfh_repo()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=seeded_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: seeded_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-999/social-family-history")

            response = run_async(do_test())

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service

    def test_get_social_family_history_no_history_documented(self):
        """Test empty response when patient exists but has no history."""
        # Use empty repo
        empty_repo = SocialFamilyHistoryRepository()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=empty_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: empty_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    # patient-001 exists in seeded patient data but has no history in our repo
                    return await client.get("/patients/patient-001/social-family-history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            # Empty structure, not 404
            assert data["socialHistory"] is None
            assert data["familyHistory"] is None
            assert data["riskAssessments"] == []
            assert data["hasHighRisk"] is False
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service

    def test_response_structure(self):
        """Test the complete response structure."""
        seeded_repo = create_seeded_sfh_repo()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=seeded_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: seeded_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/social-family-history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            # Check social history structure
            social = data["socialHistory"]
            assert "smoking" in social
            assert "alcohol" in social
            assert "substanceUse" in social
            assert "occupation" in social
            assert "maritalStatus" in social
            assert "exercise" in social

            # Check smoking structure
            assert "status" in social["smoking"]
            assert "packYears" in social["smoking"]

            # Check family history structure
            family = data["familyHistory"]
            assert "familyMembers" in family
            assert "significantConditions" in family
            assert "hereditarySyndromes" in family
            assert "adoptionStatus" in family

            # Check family member structure
            if family["familyMembers"]:
                member = family["familyMembers"][0]
                assert "id" in member
                assert "relativeType" in member
                assert "degree" in member
                assert "isLiving" in member
                assert "conditions" in member

            # Check risk assessment structure
            if data["riskAssessments"]:
                risk = data["riskAssessments"][0]
                assert "riskType" in risk
                assert "riskLevel" in risk
                assert "contributingFactors" in risk
                assert "recommendations" in risk
                assert "screeningDue" in risk
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service

    def test_risk_assessment_levels(self):
        """Test that risk assessment levels are valid."""
        seeded_repo = create_seeded_sfh_repo()
        from services.social_family_history_service import SocialFamilyHistoryService
        mock_service = SocialFamilyHistoryService(social_family_history_repo=seeded_repo)

        original_get_repo = dependencies.get_social_family_history_repo
        original_get_service = dependencies.get_social_family_history_service

        dependencies.get_social_family_history_repo = lambda: seeded_repo
        dependencies.get_social_family_history_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/social-family-history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            for risk in data["riskAssessments"]:
                assert risk["riskLevel"] in ["low", "moderate", "high"]
        finally:
            dependencies.get_social_family_history_repo = original_get_repo
            dependencies.get_social_family_history_service = original_get_service
