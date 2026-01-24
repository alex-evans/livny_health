"""
Social and Family History Service.

Provides social/family history retrieval and risk assessment calculation.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from resources import (
    SocialFamilyHistoryRepository,
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    RiskAssessment,
    RiskLevel,
)


@dataclass
class SocialFamilyHistoryResponse:
    """Response containing social/family history with risk assessments."""
    social_history: SocialHistory | None
    family_history: FamilyHistory | None
    risk_assessments: list[RiskAssessment]
    last_reviewed: datetime | None
    has_high_risk: bool

    def to_dict(self) -> dict:
        return {
            "socialHistory": self.social_history.to_dict() if self.social_history else None,
            "familyHistory": self.family_history.to_dict() if self.family_history else None,
            "riskAssessments": [ra.to_dict() for ra in self.risk_assessments],
            "lastReviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "hasHighRisk": self.has_high_risk,
        }


class SocialFamilyHistoryService:
    """
    Service for retrieving social/family history and calculating risk assessments.
    """

    def __init__(self, social_family_history_repo: SocialFamilyHistoryRepository):
        self.repo = social_family_history_repo

    async def get_social_family_history(
        self,
        patient_id: str,
        include_risk_assessments: bool = True,
    ) -> SocialFamilyHistoryResponse:
        """
        Get social/family history with optional risk assessments.

        Args:
            patient_id: The patient ID
            include_risk_assessments: Whether to calculate and include risk assessments

        Returns:
            SocialFamilyHistoryResponse with history and optional risk assessments
        """
        history = await self.repo.get_by_patient(patient_id)

        if not history:
            # Return empty response (not an error - patient may not have documented history)
            return SocialFamilyHistoryResponse(
                social_history=None,
                family_history=None,
                risk_assessments=[],
                last_reviewed=None,
                has_high_risk=False,
            )

        risk_assessments: list[RiskAssessment] = []
        if include_risk_assessments:
            risk_assessments = self._calculate_risk_assessments(
                history.social_history,
                history.family_history,
            )

        has_high_risk = any(ra.risk_level == "high" for ra in risk_assessments)

        return SocialFamilyHistoryResponse(
            social_history=history.social_history,
            family_history=history.family_history,
            risk_assessments=risk_assessments,
            last_reviewed=history.last_reviewed,
            has_high_risk=has_high_risk,
        )

    def _calculate_risk_assessments(
        self,
        social: SocialHistory,
        family: FamilyHistory,
    ) -> list[RiskAssessment]:
        """
        Calculate risk assessments based on social and family history.

        This is a simplified risk calculation. Production implementations
        would use validated clinical calculators.
        """
        risk_assessments = []

        # Calculate cardiovascular risk
        cv_risk = self._calculate_cardiovascular_risk(social, family)
        risk_assessments.append(cv_risk)

        # Calculate cancer risk
        cancer_risk = self._calculate_cancer_risk(social, family)
        risk_assessments.append(cancer_risk)

        # Calculate diabetes risk
        diabetes_risk = self._calculate_diabetes_risk(social, family)
        risk_assessments.append(diabetes_risk)

        return risk_assessments

    def _calculate_cardiovascular_risk(
        self,
        social: SocialHistory,
        family: FamilyHistory,
    ) -> RiskAssessment:
        """Calculate cardiovascular disease risk."""
        contributing_factors: list[str] = []
        recommendations: list[str] = []
        risk_score = 0

        # Smoking
        if social.smoking.status == "current_daily":
            contributing_factors.append("Current daily smoker")
            recommendations.append("Smoking cessation counseling recommended")
            risk_score += 3
        elif social.smoking.status == "current_occasional":
            contributing_factors.append("Current occasional smoker")
            recommendations.append("Smoking cessation counseling recommended")
            risk_score += 2
        elif social.smoking.status == "former":
            if social.smoking.pack_years and social.smoking.pack_years >= 10:
                contributing_factors.append(f"Former smoker with {social.smoking.pack_years} pack-years")
                risk_score += 1

        # Exercise level
        if social.exercise == "sedentary":
            contributing_factors.append("Sedentary lifestyle")
            recommendations.append("Increase physical activity to at least 150 min/week")
            risk_score += 2
        elif social.exercise == "light":
            contributing_factors.append("Light exercise only")
            recommendations.append("Consider increasing physical activity")
            risk_score += 1

        # Alcohol
        if social.alcohol.use_level == "heavy":
            contributing_factors.append("Heavy alcohol use")
            recommendations.append("Alcohol reduction counseling")
            risk_score += 1

        # Family history
        cv_conditions = {"heart disease", "hypertension", "stroke", "heart attack", "coronary artery disease"}
        for member in family.family_members:
            if member.degree == "first":
                for condition in member.conditions:
                    condition_lower = condition.condition_name.lower()
                    if any(cv in condition_lower for cv in cv_conditions):
                        contributing_factors.append(
                            f"Family history: {member.relative_type} with {condition.condition_name}"
                        )
                        # Early onset in first-degree relative
                        if condition.age_at_onset and condition.age_at_onset < 55:
                            risk_score += 2
                        else:
                            risk_score += 1
                        break  # Count each relative once

        # Determine risk level
        if risk_score >= 5:
            risk_level: RiskLevel = "high"
        elif risk_score >= 2:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Add default recommendations
        if risk_level in ("moderate", "high"):
            recommendations.append("Consider lipid panel screening")
            recommendations.append("Blood pressure monitoring recommended")

        # Calculate screening due date (annual for high risk)
        screening_interval = 6 if risk_level == "high" else 12
        screening_due = date.today() + relativedelta(months=screening_interval)

        return RiskAssessment(
            risk_type="cardiovascular",
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
            screening_due=screening_due,
            calculated_at=datetime.utcnow(),
        )

    def _calculate_cancer_risk(
        self,
        social: SocialHistory,
        family: FamilyHistory,
    ) -> RiskAssessment:
        """Calculate general cancer risk."""
        contributing_factors: list[str] = []
        recommendations: list[str] = []
        risk_score = 0

        # Smoking (lung cancer, etc.)
        if social.smoking.status in ("current_daily", "current_occasional"):
            contributing_factors.append("Current tobacco use")
            recommendations.append("Lung cancer screening may be indicated")
            risk_score += 2
        elif social.smoking.status == "former":
            if social.smoking.pack_years and social.smoking.pack_years >= 20:
                contributing_factors.append(f"Former heavy smoker ({social.smoking.pack_years} pack-years)")
                recommendations.append("Consider lung cancer screening")
                risk_score += 1

        # Alcohol
        if social.alcohol.use_level == "heavy":
            contributing_factors.append("Heavy alcohol use")
            risk_score += 1

        # Hereditary syndromes
        high_risk_syndromes = {"brca", "lynch syndrome", "hereditary", "familial"}
        for syndrome in family.hereditary_syndromes:
            syndrome_lower = syndrome.lower()
            if any(s in syndrome_lower for s in high_risk_syndromes):
                contributing_factors.append(f"Hereditary syndrome: {syndrome}")
                recommendations.append(f"Genetic counseling recommended for {syndrome}")
                risk_score += 3

        # Family history of cancer
        cancer_terms = {"cancer", "carcinoma", "melanoma", "lymphoma", "leukemia"}
        first_degree_cancers: list[str] = []
        for member in family.family_members:
            if member.degree == "first":
                for condition in member.conditions:
                    condition_lower = condition.condition_name.lower()
                    if any(c in condition_lower for c in cancer_terms):
                        first_degree_cancers.append(
                            f"{member.relative_type}: {condition.condition_name}"
                        )
                        # Early onset cancer is more concerning
                        if condition.age_at_onset and condition.age_at_onset < 50:
                            risk_score += 2
                        else:
                            risk_score += 1

        if first_degree_cancers:
            contributing_factors.append(f"Family history of cancer in first-degree relatives")
            for cancer_desc in first_degree_cancers[:3]:  # Limit to 3 for readability
                contributing_factors.append(f"  - {cancer_desc}")

        # Determine risk level
        if risk_score >= 4:
            risk_level: RiskLevel = "high"
        elif risk_score >= 2:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # General recommendations
        if risk_level in ("moderate", "high"):
            recommendations.append("Age-appropriate cancer screenings recommended")
            if risk_level == "high":
                recommendations.append("Consider enhanced screening protocols")

        # Calculate screening due date
        screening_interval = 6 if risk_level == "high" else 12
        screening_due = date.today() + relativedelta(months=screening_interval)

        return RiskAssessment(
            risk_type="cancer",
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
            screening_due=screening_due,
            calculated_at=datetime.utcnow(),
        )

    def _calculate_diabetes_risk(
        self,
        social: SocialHistory,
        family: FamilyHistory,
    ) -> RiskAssessment:
        """Calculate type 2 diabetes risk."""
        contributing_factors: list[str] = []
        recommendations: list[str] = []
        risk_score = 0

        # Exercise level
        if social.exercise == "sedentary":
            contributing_factors.append("Sedentary lifestyle")
            recommendations.append("Increase physical activity to reduce diabetes risk")
            risk_score += 2
        elif social.exercise == "light":
            contributing_factors.append("Light exercise only")
            risk_score += 1

        # Diet
        if social.diet in ("regular", "unknown"):
            # No specific dietary considerations noted
            pass
        elif social.diet == "diabetic":
            contributing_factors.append("Currently following diabetic diet")
            # This might indicate existing concerns

        # Family history
        diabetes_terms = {"diabetes", "diabetic", "glucose intolerance", "prediabetes"}
        for member in family.family_members:
            if member.degree == "first":
                for condition in member.conditions:
                    condition_lower = condition.condition_name.lower()
                    if any(d in condition_lower for d in diabetes_terms):
                        contributing_factors.append(
                            f"Family history: {member.relative_type} with {condition.condition_name}"
                        )
                        risk_score += 2
                        break  # Count each relative once
            elif member.degree == "second":
                for condition in member.conditions:
                    condition_lower = condition.condition_name.lower()
                    if any(d in condition_lower for d in diabetes_terms):
                        contributing_factors.append(
                            f"Family history: {member.relative_type} with {condition.condition_name}"
                        )
                        risk_score += 1
                        break

        # Determine risk level
        if risk_score >= 4:
            risk_level: RiskLevel = "high"
        elif risk_score >= 2:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Recommendations
        if risk_level in ("moderate", "high"):
            recommendations.append("HbA1c or fasting glucose screening recommended")
            if risk_level == "high":
                recommendations.append("Consider more frequent glucose monitoring")
                recommendations.append("Lifestyle modification counseling recommended")

        # Calculate screening due date
        screening_interval = 6 if risk_level == "high" else 12
        screening_due = date.today() + relativedelta(months=screening_interval)

        return RiskAssessment(
            risk_type="diabetes",
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
            screening_due=screening_due,
            calculated_at=datetime.utcnow(),
        )
