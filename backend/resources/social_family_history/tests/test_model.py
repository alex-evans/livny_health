"""Tests for social and family history model."""

import pytest
from datetime import datetime, date

from resources.social_family_history.model import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    SubstanceUseHistory,
    FamilyMember,
    FamilyMemberCondition,
    SignificantCondition,
    RiskAssessment,
    RELATIVE_DEGREE_MAP,
)
from resources.core import Reference


class TestSmokingHistory:
    """Tests for SmokingHistory model."""

    def test_create_smoking_history(self):
        """Test creating a smoking history."""
        smoking = SmokingHistory(
            status="former",
            pack_years=10.5,
            quit_date=date(2020, 1, 15),
            notes="Quit after 20 years",
        )

        assert smoking.status == "former"
        assert smoking.pack_years == 10.5
        assert smoking.quit_date == date(2020, 1, 15)
        assert smoking.notes == "Quit after 20 years"

    def test_smoking_history_defaults(self):
        """Test default values for smoking history."""
        smoking = SmokingHistory()

        assert smoking.status == "unknown"
        assert smoking.pack_years is None
        assert smoking.quit_date is None
        assert smoking.notes is None

    def test_smoking_history_to_dict(self):
        """Test conversion to dictionary."""
        smoking = SmokingHistory(
            status="former",
            pack_years=10.5,
            quit_date=date(2020, 1, 15),
        )

        d = smoking.to_dict()

        assert d["status"] == "former"
        assert d["packYears"] == 10.5
        assert d["quitDate"] == "2020-01-15"
        assert "notes" in d


class TestAlcoholHistory:
    """Tests for AlcoholHistory model."""

    def test_create_alcohol_history(self):
        """Test creating an alcohol history."""
        alcohol = AlcoholHistory(
            use_level="moderate",
            drinks_per_week=7,
            history_of_abuse=False,
            notes="Social drinking",
        )

        assert alcohol.use_level == "moderate"
        assert alcohol.drinks_per_week == 7
        assert alcohol.history_of_abuse is False

    def test_alcohol_history_to_dict(self):
        """Test conversion to dictionary."""
        alcohol = AlcoholHistory(
            use_level="heavy",
            drinks_per_week=20,
            history_of_abuse=True,
        )

        d = alcohol.to_dict()

        assert d["useLevel"] == "heavy"
        assert d["drinksPerWeek"] == 20
        assert d["historyOfAbuse"] is True


class TestSubstanceUseHistory:
    """Tests for SubstanceUseHistory model."""

    def test_create_substance_use_history(self):
        """Test creating a substance use history."""
        substance = SubstanceUseHistory(
            level="past",
            substances=["marijuana", "cocaine"],
            iv_drug_use=False,
            notes="Last used 10 years ago",
        )

        assert substance.level == "past"
        assert "marijuana" in substance.substances
        assert substance.iv_drug_use is False

    def test_substance_use_to_dict(self):
        """Test conversion to dictionary."""
        substance = SubstanceUseHistory(
            level="current",
            substances=["marijuana"],
            iv_drug_use=True,
        )

        d = substance.to_dict()

        assert d["level"] == "current"
        assert d["substances"] == ["marijuana"]
        assert d["ivDrugUse"] is True


class TestSocialHistory:
    """Tests for SocialHistory model."""

    def test_create_social_history(self):
        """Test creating a social history."""
        social = SocialHistory(
            smoking=SmokingHistory(status="never"),
            alcohol=AlcoholHistory(use_level="occasional"),
            occupation="Teacher",
            living_situation="Lives with spouse",
            marital_status="married",
            exercise="moderate",
            diet="heart_healthy",
            last_reviewed=datetime(2025, 1, 15),
            reviewed_by="Dr. Smith",
        )

        assert social.smoking.status == "never"
        assert social.alcohol.use_level == "occasional"
        assert social.occupation == "Teacher"
        assert social.marital_status == "married"
        assert social.exercise == "moderate"

    def test_social_history_to_dict(self):
        """Test conversion to dictionary."""
        social = SocialHistory(
            smoking=SmokingHistory(status="current_daily"),
            occupation="Engineer",
            occupation_hazards=["Prolonged sitting"],
            last_reviewed=datetime(2025, 1, 15, 10, 30),
        )

        d = social.to_dict()

        assert d["smoking"]["status"] == "current_daily"
        assert d["occupation"] == "Engineer"
        assert d["occupationHazards"] == ["Prolonged sitting"]
        assert d["lastReviewed"] is not None


class TestFamilyMemberCondition:
    """Tests for FamilyMemberCondition model."""

    def test_create_condition(self):
        """Test creating a family member condition."""
        condition = FamilyMemberCondition(
            condition_name="Type 2 diabetes",
            icd10_code="E11",
            age_at_onset=55,
            notes="Diet-controlled",
        )

        assert condition.condition_name == "Type 2 diabetes"
        assert condition.icd10_code == "E11"
        assert condition.age_at_onset == 55

    def test_condition_to_dict(self):
        """Test conversion to dictionary."""
        condition = FamilyMemberCondition(
            condition_name="Hypertension",
            icd10_code="I10",
            age_at_onset=45,
        )

        d = condition.to_dict()

        assert d["conditionName"] == "Hypertension"
        assert d["icd10Code"] == "I10"
        assert d["ageAtOnset"] == 45


class TestFamilyMember:
    """Tests for FamilyMember model."""

    def test_create_family_member(self):
        """Test creating a family member."""
        member = FamilyMember(
            id="fm-1",
            relative_type="father",
            is_living=True,
            conditions=[
                FamilyMemberCondition(condition_name="Diabetes", icd10_code="E11"),
            ],
        )

        assert member.id == "fm-1"
        assert member.relative_type == "father"
        assert member.is_living is True
        assert len(member.conditions) == 1

    def test_deceased_family_member(self):
        """Test creating a deceased family member."""
        member = FamilyMember(
            id="fm-2",
            relative_type="maternal_grandmother",
            is_living=False,
            age_at_death=78,
            cause_of_death="Heart attack",
        )

        assert member.is_living is False
        assert member.age_at_death == 78
        assert member.cause_of_death == "Heart attack"

    def test_family_member_degree(self):
        """Test degree property for different relatives."""
        first_degree = FamilyMember(id="1", relative_type="mother")
        second_degree = FamilyMember(id="2", relative_type="maternal_aunt")
        third_degree = FamilyMember(id="3", relative_type="cousin")

        assert first_degree.degree == "first"
        assert second_degree.degree == "second"
        assert third_degree.degree == "third"

    def test_family_member_to_dict(self):
        """Test conversion to dictionary."""
        member = FamilyMember(
            id="fm-1",
            relative_type="brother",
            is_living=True,
            conditions=[
                FamilyMemberCondition(condition_name="Asthma"),
            ],
        )

        d = member.to_dict()

        assert d["id"] == "fm-1"
        assert d["relativeType"] == "brother"
        assert d["degree"] == "first"
        assert d["isLiving"] is True
        assert len(d["conditions"]) == 1


class TestSignificantCondition:
    """Tests for SignificantCondition model."""

    def test_create_significant_condition(self):
        """Test creating a significant condition."""
        condition = SignificantCondition(
            condition_name="Breast cancer",
            icd10_code="C50.9",
            affected_relatives=["mother", "maternal_grandmother"],
            notes="Two generations affected",
        )

        assert condition.condition_name == "Breast cancer"
        assert len(condition.affected_relatives) == 2

    def test_significant_condition_to_dict(self):
        """Test conversion to dictionary."""
        condition = SignificantCondition(
            condition_name="Diabetes",
            icd10_code="E11",
            affected_relatives=["father", "grandfather"],
        )

        d = condition.to_dict()

        assert d["conditionName"] == "Diabetes"
        assert d["icd10Code"] == "E11"
        assert d["affectedRelatives"] == ["father", "grandfather"]


class TestFamilyHistory:
    """Tests for FamilyHistory model."""

    def test_create_family_history(self):
        """Test creating a family history."""
        family = FamilyHistory(
            family_members=[
                FamilyMember(id="1", relative_type="father"),
                FamilyMember(id="2", relative_type="mother"),
            ],
            significant_conditions=[
                SignificantCondition(condition_name="Heart disease"),
            ],
            hereditary_syndromes=["BRCA1"],
            adoption_status="not_adopted",
            last_reviewed=datetime(2025, 1, 15),
        )

        assert len(family.family_members) == 2
        assert len(family.significant_conditions) == 1
        assert "BRCA1" in family.hereditary_syndromes

    def test_family_history_to_dict(self):
        """Test conversion to dictionary."""
        family = FamilyHistory(
            family_members=[FamilyMember(id="1", relative_type="father")],
            hereditary_syndromes=["Lynch syndrome"],
            adoption_status="adopted_known_history",
        )

        d = family.to_dict()

        assert len(d["familyMembers"]) == 1
        assert d["hereditarySyndromes"] == ["Lynch syndrome"]
        assert d["adoptionStatus"] == "adopted_known_history"


class TestRiskAssessment:
    """Tests for RiskAssessment model."""

    def test_create_risk_assessment(self):
        """Test creating a risk assessment."""
        risk = RiskAssessment(
            risk_type="cardiovascular",
            risk_level="high",
            contributing_factors=["smoking", "family history"],
            recommendations=["Quit smoking", "Exercise"],
            screening_due=date(2025, 6, 15),
        )

        assert risk.risk_type == "cardiovascular"
        assert risk.risk_level == "high"
        assert len(risk.contributing_factors) == 2
        assert len(risk.recommendations) == 2

    def test_risk_assessment_to_dict(self):
        """Test conversion to dictionary."""
        risk = RiskAssessment(
            risk_type="diabetes",
            risk_level="moderate",
            contributing_factors=["sedentary lifestyle"],
            recommendations=["Increase activity"],
            screening_due=date(2025, 12, 1),
            calculated_at=datetime(2025, 1, 15, 10, 30),
        )

        d = risk.to_dict()

        assert d["riskType"] == "diabetes"
        assert d["riskLevel"] == "moderate"
        assert d["contributingFactors"] == ["sedentary lifestyle"]
        assert d["screeningDue"] == "2025-12-01"
        assert "calculatedAt" in d


class TestSocialFamilyHistory:
    """Tests for SocialFamilyHistory model."""

    def test_create_social_family_history(self):
        """Test creating a complete social/family history."""
        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="former"),
                occupation="Teacher",
            ),
            family_history=FamilyHistory(
                family_members=[FamilyMember(id="1", relative_type="father")],
            ),
            risk_assessments=[
                RiskAssessment(risk_type="cardiovascular", risk_level="moderate"),
            ],
        )

        assert history.id == "sfh-1"
        assert history.patient_id == "patient-001"
        assert history.social_history.smoking.status == "former"
        assert len(history.family_history.family_members) == 1
        assert len(history.risk_assessments) == 1

    def test_patient_id_property(self):
        """Test patient_id property extraction."""
        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-123", "Test"),
        )

        assert history.patient_id == "patient-123"

    def test_last_reviewed_property(self):
        """Test last_reviewed returns most recent date."""
        social_reviewed = datetime(2025, 1, 10)
        family_reviewed = datetime(2025, 1, 15)

        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test"),
            social_history=SocialHistory(last_reviewed=social_reviewed),
            family_history=FamilyHistory(last_reviewed=family_reviewed),
        )

        assert history.last_reviewed == family_reviewed

    def test_last_reviewed_with_only_social(self):
        """Test last_reviewed when only social has date."""
        social_reviewed = datetime(2025, 1, 10)

        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test"),
            social_history=SocialHistory(last_reviewed=social_reviewed),
        )

        assert history.last_reviewed == social_reviewed

    def test_last_reviewed_with_neither(self):
        """Test last_reviewed when neither has date."""
        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test"),
        )

        assert history.last_reviewed is None

    def test_has_high_risk_property(self):
        """Test has_high_risk property."""
        history_high = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test"),
            risk_assessments=[
                RiskAssessment(risk_type="cardiovascular", risk_level="high"),
            ],
        )

        history_low = SocialFamilyHistory(
            id="sfh-2",
            subject=Reference.to("Patient", "patient-001", "Test"),
            risk_assessments=[
                RiskAssessment(risk_type="cardiovascular", risk_level="low"),
            ],
        )

        assert history_high.has_high_risk is True
        assert history_low.has_high_risk is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test"),
            social_history=SocialHistory(occupation="Teacher"),
            family_history=FamilyHistory(adoption_status="not_adopted"),
            risk_assessments=[
                RiskAssessment(risk_type="cardiovascular", risk_level="low"),
            ],
        )

        d = history.to_dict()

        assert d["id"] == "sfh-1"
        assert d["resourceType"] == "SocialFamilyHistory"
        assert "socialHistory" in d
        assert "familyHistory" in d
        assert "riskAssessments" in d
        assert "hasHighRisk" in d

    def test_to_bff_dict(self):
        """Test conversion to BFF format."""
        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test"),
            social_history=SocialHistory(occupation="Teacher"),
            risk_assessments=[
                RiskAssessment(risk_type="cardiovascular", risk_level="moderate"),
            ],
        )

        d = history.to_bff_dict()

        assert "socialHistory" in d
        assert "familyHistory" in d
        assert "riskAssessments" in d
        assert "hasHighRisk" in d
        # BFF dict doesn't include id or subject
        assert "id" not in d
        assert "subject" not in d


class TestRelativeDegreeMap:
    """Tests for RELATIVE_DEGREE_MAP configuration."""

    def test_first_degree_relatives(self):
        """Test that first-degree relatives are correctly mapped."""
        first_degree = ["mother", "father", "sister", "brother", "daughter", "son"]
        for relative in first_degree:
            assert RELATIVE_DEGREE_MAP.get(relative) == "first", f"{relative} should be first-degree"

    def test_second_degree_relatives(self):
        """Test that second-degree relatives are correctly mapped."""
        second_degree = [
            "maternal_grandmother",
            "maternal_grandfather",
            "paternal_grandmother",
            "paternal_grandfather",
            "maternal_aunt",
            "maternal_uncle",
            "paternal_aunt",
            "paternal_uncle",
            "half_sibling",
            "niece",
            "nephew",
        ]
        for relative in second_degree:
            assert RELATIVE_DEGREE_MAP.get(relative) == "second", f"{relative} should be second-degree"

    def test_third_degree_relatives(self):
        """Test that third-degree relatives are correctly mapped."""
        third_degree = ["cousin", "other"]
        for relative in third_degree:
            assert RELATIVE_DEGREE_MAP.get(relative) == "third", f"{relative} should be third-degree"
