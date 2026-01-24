"""Tests for social family history service."""

import asyncio
import pytest
from datetime import datetime, date

from resources.social_family_history import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    SubstanceUseHistory,
    FamilyMember,
    FamilyMemberCondition,
    SignificantCondition,
    SocialFamilyHistoryRepository,
)
from resources.core import Reference
from services.social_family_history_service import SocialFamilyHistoryService


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def repo():
    """Create a fresh repository for each test."""
    return SocialFamilyHistoryRepository()


@pytest.fixture
def service(repo):
    """Create a service with the repository."""
    return SocialFamilyHistoryService(social_family_history_repo=repo)


@pytest.fixture
def seeded_repo():
    """Create a repository with sample data."""
    repo = SocialFamilyHistoryRepository()

    # Patient with high cardiovascular risk
    high_cv_risk = SocialFamilyHistory(
        id="sfh-001",
        subject=Reference.to("Patient", "patient-001", "High Risk Patient"),
        social_history=SocialHistory(
            smoking=SmokingHistory(status="current_daily", pack_years=20),
            alcohol=AlcoholHistory(use_level="heavy", drinks_per_week=21),
            exercise="sedentary",
        ),
        family_history=FamilyHistory(
            family_members=[
                FamilyMember(
                    id="fm-1",
                    relative_type="father",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Heart disease",
                            age_at_onset=50,
                        ),
                    ],
                ),
            ],
        ),
    )

    # Patient with low risk
    low_risk = SocialFamilyHistory(
        id="sfh-002",
        subject=Reference.to("Patient", "patient-002", "Low Risk Patient"),
        social_history=SocialHistory(
            smoking=SmokingHistory(status="never"),
            alcohol=AlcoholHistory(use_level="occasional", drinks_per_week=2),
            exercise="active",
        ),
        family_history=FamilyHistory(
            family_members=[],
        ),
    )

    # Patient with diabetes risk
    diabetes_risk = SocialFamilyHistory(
        id="sfh-003",
        subject=Reference.to("Patient", "patient-003", "Diabetes Risk Patient"),
        social_history=SocialHistory(
            smoking=SmokingHistory(status="never"),
            exercise="sedentary",
        ),
        family_history=FamilyHistory(
            family_members=[
                FamilyMember(
                    id="fm-2",
                    relative_type="mother",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Type 2 diabetes",
                            age_at_onset=55,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-3",
                    relative_type="father",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Type 2 diabetes",
                            age_at_onset=60,
                        ),
                    ],
                ),
            ],
        ),
    )

    # Patient with cancer risk (hereditary syndrome)
    cancer_risk = SocialFamilyHistory(
        id="sfh-004",
        subject=Reference.to("Patient", "patient-004", "Cancer Risk Patient"),
        social_history=SocialHistory(
            smoking=SmokingHistory(status="former", pack_years=25),
        ),
        family_history=FamilyHistory(
            family_members=[
                FamilyMember(
                    id="fm-4",
                    relative_type="mother",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Breast cancer",
                            age_at_onset=45,
                        ),
                    ],
                ),
            ],
            hereditary_syndromes=["BRCA1 mutation"],
        ),
    )

    repo._store["sfh-001"] = high_cv_risk
    repo._store["sfh-002"] = low_risk
    repo._store["sfh-003"] = diabetes_risk
    repo._store["sfh-004"] = cancer_risk

    return repo


@pytest.fixture
def seeded_service(seeded_repo):
    """Create a service with seeded data."""
    return SocialFamilyHistoryService(social_family_history_repo=seeded_repo)


@pytest.mark.unit
class TestGetSocialFamilyHistory:
    """Tests for get_social_family_history method."""

    def test_returns_history(self, seeded_service):
        """Test that history is returned for existing patient."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        assert response.social_history is not None
        assert response.family_history is not None
        assert response.social_history.smoking.status == "current_daily"

    def test_returns_risk_assessments_by_default(self, seeded_service):
        """Test that risk assessments are included by default."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        assert len(response.risk_assessments) == 3  # CV, cancer, diabetes
        risk_types = {ra.risk_type for ra in response.risk_assessments}
        assert "cardiovascular" in risk_types
        assert "cancer" in risk_types
        assert "diabetes" in risk_types

    def test_exclude_risk_assessments(self, seeded_service):
        """Test excluding risk assessments."""
        response = run_async(seeded_service.get_social_family_history(
            "patient-001",
            include_risk_assessments=False,
        ))

        assert len(response.risk_assessments) == 0

    def test_empty_response_for_unknown_patient(self, seeded_service):
        """Test empty response for patient without history."""
        response = run_async(seeded_service.get_social_family_history("patient-999"))

        assert response.social_history is None
        assert response.family_history is None
        assert len(response.risk_assessments) == 0
        assert response.last_reviewed is None
        assert response.has_high_risk is False

    def test_to_dict(self, seeded_service):
        """Test response conversion to dictionary."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        d = response.to_dict()

        assert "socialHistory" in d
        assert "familyHistory" in d
        assert "riskAssessments" in d
        assert "lastReviewed" in d
        assert "hasHighRisk" in d


@pytest.mark.unit
class TestCardiovascularRiskCalculation:
    """Tests for cardiovascular risk calculation."""

    def test_high_risk_current_smoker(self, seeded_service):
        """Test high CV risk for current smoker with family history."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert cv_risk is not None
        assert cv_risk.risk_level == "high"
        assert any("smoker" in f.lower() for f in cv_risk.contributing_factors)

    def test_low_risk_never_smoker_active(self, seeded_service):
        """Test low CV risk for never smoker with active lifestyle."""
        response = run_async(seeded_service.get_social_family_history("patient-002"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert cv_risk is not None
        assert cv_risk.risk_level == "low"

    def test_sedentary_lifestyle_factor(self, seeded_service):
        """Test that sedentary lifestyle is noted as contributing factor."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert any("sedentary" in f.lower() for f in cv_risk.contributing_factors)

    def test_family_history_factor(self, seeded_service):
        """Test that family history is noted as contributing factor."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert any("family history" in f.lower() for f in cv_risk.contributing_factors)

    def test_recommendations_for_high_risk(self, seeded_service):
        """Test that recommendations are provided for high risk."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert len(cv_risk.recommendations) > 0
        assert any("smoking" in r.lower() for r in cv_risk.recommendations)


@pytest.mark.unit
class TestCancerRiskCalculation:
    """Tests for cancer risk calculation."""

    def test_high_risk_hereditary_syndrome(self, seeded_service):
        """Test high cancer risk for patient with hereditary syndrome."""
        response = run_async(seeded_service.get_social_family_history("patient-004"))

        cancer_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cancer"), None)
        assert cancer_risk is not None
        assert cancer_risk.risk_level == "high"
        assert any("brca" in f.lower() for f in cancer_risk.contributing_factors)

    def test_former_heavy_smoker_factor(self, seeded_service):
        """Test that former heavy smoking is noted."""
        response = run_async(seeded_service.get_social_family_history("patient-004"))

        cancer_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cancer"), None)
        assert any("former" in f.lower() and "smoker" in f.lower() for f in cancer_risk.contributing_factors)

    def test_family_cancer_history(self, seeded_service):
        """Test family history of cancer is noted."""
        response = run_async(seeded_service.get_social_family_history("patient-004"))

        cancer_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cancer"), None)
        assert any("family history" in f.lower() and "cancer" in f.lower() for f in cancer_risk.contributing_factors)

    def test_genetic_counseling_recommendation(self, seeded_service):
        """Test genetic counseling recommendation for hereditary syndrome."""
        response = run_async(seeded_service.get_social_family_history("patient-004"))

        cancer_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cancer"), None)
        assert any("genetic counseling" in r.lower() for r in cancer_risk.recommendations)


@pytest.mark.unit
class TestDiabetesRiskCalculation:
    """Tests for diabetes risk calculation."""

    def test_high_risk_family_history(self, seeded_service):
        """Test high diabetes risk with strong family history."""
        response = run_async(seeded_service.get_social_family_history("patient-003"))

        diabetes_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "diabetes"), None)
        assert diabetes_risk is not None
        assert diabetes_risk.risk_level == "high"

    def test_sedentary_lifestyle_factor(self, seeded_service):
        """Test that sedentary lifestyle is noted for diabetes risk."""
        response = run_async(seeded_service.get_social_family_history("patient-003"))

        diabetes_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "diabetes"), None)
        assert any("sedentary" in f.lower() for f in diabetes_risk.contributing_factors)

    def test_family_diabetes_history(self, seeded_service):
        """Test family history of diabetes is noted."""
        response = run_async(seeded_service.get_social_family_history("patient-003"))

        diabetes_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "diabetes"), None)
        assert any("family history" in f.lower() for f in diabetes_risk.contributing_factors)

    def test_glucose_screening_recommendation(self, seeded_service):
        """Test glucose screening is recommended for high risk."""
        response = run_async(seeded_service.get_social_family_history("patient-003"))

        diabetes_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "diabetes"), None)
        assert any("glucose" in r.lower() or "hba1c" in r.lower() for r in diabetes_risk.recommendations)


@pytest.mark.unit
class TestHasHighRisk:
    """Tests for has_high_risk calculation."""

    def test_has_high_risk_true(self, seeded_service):
        """Test has_high_risk is true when any risk is high."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        assert response.has_high_risk is True

    def test_has_high_risk_false(self, seeded_service):
        """Test has_high_risk is false when no risk is high."""
        response = run_async(seeded_service.get_social_family_history("patient-002"))

        assert response.has_high_risk is False


@pytest.mark.unit
class TestScreeningDueDates:
    """Tests for screening due date calculation."""

    def test_high_risk_shorter_interval(self, seeded_service):
        """Test that high risk patients have shorter screening intervals."""
        response = run_async(seeded_service.get_social_family_history("patient-001"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert cv_risk.screening_due is not None
        # High risk should be 6 months
        expected_date = date.today()
        months_until_due = (cv_risk.screening_due.year - expected_date.year) * 12 + (cv_risk.screening_due.month - expected_date.month)
        assert months_until_due <= 6

    def test_low_risk_longer_interval(self, seeded_service):
        """Test that low risk patients have longer screening intervals."""
        response = run_async(seeded_service.get_social_family_history("patient-002"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        assert cv_risk.screening_due is not None
        # Low risk should be 12 months
        expected_date = date.today()
        months_until_due = (cv_risk.screening_due.year - expected_date.year) * 12 + (cv_risk.screening_due.month - expected_date.month)
        assert months_until_due >= 11  # Allow for day-of-month differences


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_family_history(self, service, repo):
        """Test risk calculation with empty family history."""
        history = SocialFamilyHistory(
            id="sfh-test",
            subject=Reference.to("Patient", "test-patient", "Test"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="never"),
                exercise="active",
            ),
            family_history=FamilyHistory(family_members=[]),
        )
        repo._store["sfh-test"] = history

        response = run_async(service.get_social_family_history("test-patient"))

        assert len(response.risk_assessments) == 3
        # All should be low risk
        for ra in response.risk_assessments:
            assert ra.risk_level == "low"

    def test_former_smoker_with_low_pack_years(self, service, repo):
        """Test former smoker with low pack years."""
        history = SocialFamilyHistory(
            id="sfh-test",
            subject=Reference.to("Patient", "test-patient", "Test"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="former", pack_years=5),
                exercise="active",
            ),
        )
        repo._store["sfh-test"] = history

        response = run_async(service.get_social_family_history("test-patient"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        # Low pack years former smoker shouldn't contribute to risk
        assert cv_risk.risk_level == "low"

    def test_multiple_first_degree_relatives_with_same_condition(self, service, repo):
        """Test counting family members correctly."""
        history = SocialFamilyHistory(
            id="sfh-test",
            subject=Reference.to("Patient", "test-patient", "Test"),
            social_history=SocialHistory(),
            family_history=FamilyHistory(
                family_members=[
                    FamilyMember(
                        id="1",
                        relative_type="father",
                        conditions=[FamilyMemberCondition(condition_name="Heart disease")],
                    ),
                    FamilyMember(
                        id="2",
                        relative_type="mother",
                        conditions=[FamilyMemberCondition(condition_name="Heart disease")],
                    ),
                ],
            ),
        )
        repo._store["sfh-test"] = history

        response = run_async(service.get_social_family_history("test-patient"))

        cv_risk = next((ra for ra in response.risk_assessments if ra.risk_type == "cardiovascular"), None)
        # Multiple first-degree relatives should increase risk
        assert cv_risk.risk_level in ("moderate", "high")
