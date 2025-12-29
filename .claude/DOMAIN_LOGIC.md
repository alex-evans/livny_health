# Domain Logic and Business Rules

This document contains examples of business logic patterns for Livny Health services. These are healthcare-specific rules that must be enforced consistently.

## Clinical Decision Support (CDS) Rules

### Allergy Checking

```python
# cds_service/domain/allergy_check.py
from typing import List, Optional
from models.drug import Drug
from models.allergy import Allergy

class AllergyChecker:
    """
    Business rules for checking drug allergies.
    
    Clinical knowledge encoded as business logic.
    """
    
    # Cross-reactivity map (clinical knowledge)
    CROSS_REACTIVITY = {
        "penicillin": [
            "amoxicillin", "ampicillin", "penicillin", "piperacillin",
            "oxacillin", "nafcillin", "dicloxacillin"
        ],
        "sulfa": [
            "sulfamethoxazole", "sulfasalazine", "sulfadiazine",
            "sulfisoxazole"
        ],
        "cephalosporin": [
            "cephalexin", "cefazolin", "ceftriaxone", "cefuroxime",
            "cefpodoxime", "cefixime"
        ],
        # ~10% cross-reactivity between penicillin and cephalosporins
        "penicillin_cephalosporin": [
            "cephalexin", "cefazolin", "ceftriaxone"
        ]
    }
    
    @classmethod
    def check_allergy(
        cls,
        drug: Drug,
        allergies: List[Allergy]
    ) -> Optional[dict]:
        """
        Check if drug is contraindicated by allergies.
        
        Returns alert dict if contraindicated, None otherwise.
        """
        for allergy in allergies:
            # Direct match
            if cls._is_direct_match(drug, allergy):
                return {
                    "severity": "critical",
                    "type": "allergy",
                    "title": f"{allergy.allergen.title()} Allergy",
                    "message": (
                        f"Patient has documented {allergy.allergen} allergy "
                        f"with {allergy.reaction} reaction. "
                        f"{drug.name} is contraindicated."
                    ),
                    "recommendation": "Select alternative medication",
                    "references": ["AHFS Drug Information"]
                }
            
            # Cross-reactivity
            if cls._is_cross_reactive(drug, allergy):
                return {
                    "severity": "critical",
                    "type": "cross_reactivity",
                    "title": "Cross-Reactivity Alert",
                    "message": (
                        f"Patient has {allergy.allergen} allergy. "
                        f"{drug.name} may have cross-reactivity."
                    ),
                    "recommendation": (
                        "Consider alternative medication or proceed with "
                        "caution if benefit outweighs risk"
                    ),
                    "references": ["Drug Allergy: Practice Parameters"]
                }
        
        return None
    
    @classmethod
    def _is_direct_match(cls, drug: Drug, allergy: Allergy) -> bool:
        """Check if drug directly matches allergen"""
        drug_name = drug.generic_name.lower()
        allergen = allergy.allergen.lower()
        
        return drug_name == allergen or allergen in drug_name
    
    @classmethod
    def _is_cross_reactive(cls, drug: Drug, allergy: Allergy) -> bool:
        """Check if drug has cross-reactivity with allergen"""
        allergen = allergy.allergen.lower()
        drug_name = drug.generic_name.lower()
        
        # Check cross-reactivity map
        if allergen in cls.CROSS_REACTIVITY:
            if drug_name in cls.CROSS_REACTIVITY[allergen]:
                return True
        
        # Special case: penicillin allergy + cephalosporin
        if allergen == "penicillin":
            if any(ceph in drug_name for ceph in cls.CROSS_REACTIVITY["cephalosporin"]):
                # Only flag if severe penicillin reaction
                if allergy.severity in ["severe", "anaphylaxis"]:
                    return True
        
        return False
```

### Drug Interaction Checking

```python
# cds_service/domain/interaction_check.py
from typing import List, Optional
from models.drug import Drug

class InteractionChecker:
    """
    Business rules for checking drug-drug interactions.
    
    Based on clinical drug interaction databases.
    """
    
    # Major interactions (clinical significance)
    MAJOR_INTERACTIONS = {
        ("warfarin", "amoxicillin"): {
            "severity": "moderate",
            "description": "Amoxicillin may increase warfarin anticoagulant effects",
            "mechanism": "Alteration of gut flora affecting vitamin K",
            "recommendation": "Monitor INR closely, adjust warfarin dose if needed",
            "references": ["Lexicomp Drug Interactions"]
        },
        ("warfarin", "azithromycin"): {
            "severity": "major",
            "description": "Azithromycin significantly increases warfarin effects",
            "mechanism": "CYP3A4 inhibition",
            "recommendation": "Monitor INR closely, consider dose reduction",
            "references": ["Lexicomp Drug Interactions"]
        },
        ("lisinopril", "potassium"): {
            "severity": "major",
            "description": "ACE inhibitors increase risk of hyperkalemia with potassium",
            "mechanism": "Decreased renal potassium excretion",
            "recommendation": "Monitor potassium levels, avoid combination if possible",
            "references": ["AHFS Drug Information"]
        },
        ("metformin", "contrast"): {
            "severity": "major",
            "description": "Iodinated contrast may increase metformin lactic acidosis risk",
            "mechanism": "Acute kidney injury from contrast",
            "recommendation": "Hold metformin 48 hours before and after contrast",
            "references": ["ACR Manual on Contrast Media"]
        }
    }
    
    @classmethod
    async def check_interactions(
        cls,
        new_drug: Drug,
        current_medications: List[dict]
    ) -> List[dict]:
        """
        Check for drug-drug interactions.
        
        Returns list of interaction alerts.
        """
        alerts = []
        
        for med in current_medications:
            interaction = cls._find_interaction(
                new_drug.generic_name,
                med["generic_name"]
            )
            
            if interaction:
                alerts.append({
                    "severity": cls._map_severity(interaction["severity"]),
                    "type": "drug_interaction",
                    "title": f"Interaction: {med['name']}",
                    "message": interaction["description"],
                    "mechanism": interaction["mechanism"],
                    "recommendation": interaction["recommendation"],
                    "references": interaction["references"]
                })
        
        return alerts
    
    @classmethod
    def _find_interaction(
        cls,
        drug1: str,
        drug2: str
    ) -> Optional[dict]:
        """Find interaction between two drugs"""
        # Normalize names
        drug1 = drug1.lower()
        drug2 = drug2.lower()
        
        # Check both orderings
        key1 = (drug1, drug2)
        key2 = (drug2, drug1)
        
        if key1 in cls.MAJOR_INTERACTIONS:
            return cls.MAJOR_INTERACTIONS[key1]
        if key2 in cls.MAJOR_INTERACTIONS:
            return cls.MAJOR_INTERACTIONS[key2]
        
        # TODO: Query interaction database for comprehensive checking
        return None
    
    @classmethod
    def _map_severity(cls, clinical_severity: str) -> str:
        """Map clinical severity to alert severity"""
        mapping = {
            "contraindicated": "critical",
            "major": "critical",
            "moderate": "warning",
            "minor": "info"
        }
        return mapping.get(clinical_severity, "info")
```

### Renal Dosing

```python
# cds_service/domain/renal_dosing.py
from typing import Optional, Tuple
from models.drug import Drug
from models.lab_result import LabResult

class RenalDosingChecker:
    """
    Business rules for renal dose adjustments.
    
    Based on kidney function (eGFR/CrCl).
    """
    
    @classmethod
    def check_renal_dosing(
        cls,
        drug: Drug,
        creatinine: Optional[float],
        age: int,
        sex: str,
        weight_kg: float
    ) -> Optional[dict]:
        """
        Check if renal dose adjustment needed.
        
        Args:
            drug: Drug being prescribed
            creatinine: Serum creatinine (mg/dL)
            age: Patient age
            sex: Patient sex
            weight_kg: Patient weight in kg
        
        Returns:
            Alert dict if adjustment needed, None otherwise
        """
        if not drug.requires_renal_adjustment:
            return None
        
        if creatinine is None:
            return {
                "severity": "warning",
                "type": "renal_dosing",
                "title": "Renal Function Unknown",
                "message": (
                    f"{drug.name} requires renal dose adjustment. "
                    "No recent creatinine available."
                ),
                "recommendation": "Check creatinine before prescribing"
            }
        
        # Calculate creatinine clearance
        crcl = cls._calculate_crcl(creatinine, age, sex, weight_kg)
        
        # Determine if adjustment needed
        needs_adjustment, recommended_dose = cls._check_adjustment(drug, crcl)
        
        if needs_adjustment:
            severity = "warning" if crcl >= 30 else "critical"
            
            return {
                "severity": severity,
                "type": "renal_dosing",
                "title": "Renal Dose Adjustment Recommended",
                "message": (
                    f"Patient's CrCl is {crcl:.1f} mL/min. "
                    f"Renal dose adjustment recommended for {drug.name}."
                ),
                "recommendation": f"Suggested dose: {recommended_dose}",
                "references": ["Lexicomp Renal Dosing"]
            }
        
        return None
    
    @classmethod
    def _calculate_crcl(
        cls,
        creatinine: float,
        age: int,
        sex: str,
        weight_kg: float
    ) -> float:
        """
        Calculate creatinine clearance using Cockcroft-Gault.
        
        CrCl = ((140 - age) × weight × (0.85 if female)) / (72 × SCr)
        """
        crcl = ((140 - age) * weight_kg) / (72 * creatinine)
        
        if sex.lower() == "female":
            crcl *= 0.85
        
        return crcl
    
    @classmethod
    def _check_adjustment(
        cls,
        drug: Drug,
        crcl: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if adjustment needed based on CrCl.
        
        Returns:
            (needs_adjustment, recommended_dose)
        """
        # Normal renal function (>80 mL/min)
        if crcl >= 80:
            return False, None
        
        # Mild impairment (50-80 mL/min)
        if 50 <= crcl < 80:
            if drug.mild_renal_dose:
                return True, drug.mild_renal_dose
        
        # Moderate impairment (30-50 mL/min)
        if 30 <= crcl < 50:
            if drug.moderate_renal_dose:
                return True, drug.moderate_renal_dose
        
        # Severe impairment (<30 mL/min)
        if crcl < 30:
            if drug.severe_renal_dose:
                return True, drug.severe_renal_dose
            else:
                return True, "Avoid or use with extreme caution"
        
        return False, None
```

## Prescription Business Rules

### Duplicate Therapy Checking

```python
# medication_service/domain/duplicate_therapy.py
from typing import List
from models.prescription import Prescription
from models.drug import Drug

class DuplicateTherapyChecker:
    """
    Business rules for detecting duplicate therapy.
    
    Prevents prescribing multiple drugs in same class.
    """
    
    @classmethod
    def check_duplicate_therapy(
        cls,
        new_drug: Drug,
        current_prescriptions: List[Prescription]
    ) -> Optional[dict]:
        """
        Check if new drug duplicates existing therapy.
        
        Returns error if duplicate found.
        """
        for rx in current_prescriptions:
            # Same drug
            if rx.drug_id == new_drug.id:
                return {
                    "code": "duplicate_prescription",
                    "message": (
                        f"Patient already has active prescription for {new_drug.name}"
                    )
                }
            
            # Same therapeutic class
            if rx.therapeutic_class == new_drug.therapeutic_class:
                return {
                    "code": "duplicate_therapy",
                    "message": (
                        f"Patient already on {rx.drug_name} "
                        f"({new_drug.therapeutic_class}). "
                        f"Duplicate therapy detected."
                    ),
                    "existing_drug": rx.drug_name,
                    "existing_prescription_id": rx.id
                }
        
        return None
```

### Controlled Substance Rules

```python
# medication_service/domain/controlled_substances.py
from models.drug import Drug
from models.user import User

class ControlledSubstanceRules:
    """
    Business rules for controlled substance prescribing.
    
    DEA regulations and state requirements.
    """
    
    @classmethod
    def validate_prescriber(cls, drug: Drug, prescriber: User) -> None:
        """
        Validate prescriber can prescribe controlled substance.
        
        Raises exception if not authorized.
        """
        if not drug.is_controlled:
            return  # Not a controlled substance
        
        # Business rule: DEA number required
        if not prescriber.has_dea_number:
            raise ValueError(
                f"DEA number required to prescribe {drug.name} "
                f"(Schedule {drug.schedule})"
            )
        
        # Business rule: Schedule II restrictions
        if drug.schedule == "II":
            # No refills allowed on Schedule II
            if prescriber.default_refills > 0:
                raise ValueError(
                    "Schedule II controlled substances cannot have refills"
                )
            
            # Limited quantity (typically 30-day supply)
            # This would be enforced in dosage calculation
    
    @classmethod
    def calculate_max_quantity(cls, drug: Drug, duration_days: int) -> int:
        """
        Calculate maximum allowable quantity.
        
        Business rule: Controlled substances limited to 30-90 days.
        """
        if not drug.is_controlled:
            return None  # No limit
        
        if drug.schedule == "II":
            # Schedule II limited to 30 days
            max_days = 30
        else:
            # Schedule III-V limited to 90 days
            max_days = 90
        
        if duration_days > max_days:
            raise ValueError(
                f"Schedule {drug.schedule} controlled substances "
                f"limited to {max_days} day supply"
            )
        
        return duration_days
```

## Patient Safety Rules

### Age-Based Dosing

```python
# medication_service/domain/age_dosing.py
from models.drug import Drug
from datetime import datetime

class AgeDosing:
    """
    Business rules for age-based dosing.
    
    Pediatric and geriatric considerations.
    """
    
    @classmethod
    def check_age_appropriateness(
        cls,
        drug: Drug,
        patient_birth_date: datetime,
        dosage: str
    ) -> Optional[dict]:
        """
        Check if drug/dose appropriate for patient age.
        
        Returns alert if adjustment needed.
        """
        age = cls._calculate_age(patient_birth_date)
        
        # Pediatric check
        if age < 18:
            if not drug.pediatric_approved:
                return {
                    "severity": "warning",
                    "type": "pediatric",
                    "title": "Pediatric Use Caution",
                    "message": (
                        f"{drug.name} safety and efficacy not established "
                        f"in pediatric patients"
                    ),
                    "recommendation": "Consider alternative or use with caution"
                }
            
            # Check pediatric dosing
            if drug.pediatric_max_dose:
                amount = float(dosage.rstrip('mg'))
                if amount > drug.pediatric_max_dose:
                    return {
                        "severity": "critical",
                        "type": "pediatric_dosing",
                        "title": "Pediatric Dose Exceeded",
                        "message": (
                            f"Dose exceeds pediatric maximum of "
                            f"{drug.pediatric_max_dose}mg"
                        ),
                        "recommendation": f"Reduce dose to ≤{drug.pediatric_max_dose}mg"
                    }
        
        # Geriatric check
        if age >= 65:
            if drug.geriatric_considerations:
                return {
                    "severity": "info",
                    "type": "geriatric",
                    "title": "Geriatric Considerations",
                    "message": drug.geriatric_considerations,
                    "recommendation": "Start at lower dose and titrate carefully"
                }
        
        return None
    
    @classmethod
    def _calculate_age(cls, birth_date: datetime) -> int:
        """Calculate age in years"""
        today = datetime.now()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
```

### Pregnancy/Breastfeeding

```python
# medication_service/domain/pregnancy.py
from models.drug import Drug

class PregnancyChecker:
    """
    Business rules for pregnancy/breastfeeding safety.
    
    Based on FDA pregnancy categories and lactation risk.
    """
    
    PREGNANCY_CATEGORIES = {
        "A": "Adequate, well-controlled studies show no risk",
        "B": "Animal studies show no risk, but human studies inadequate",
        "C": "Animal studies show risk, human studies inadequate",
        "D": "Positive evidence of risk, but benefits may outweigh risks",
        "X": "Contraindicated in pregnancy"
    }
    
    @classmethod
    def check_pregnancy_risk(
        cls,
        drug: Drug,
        patient_sex: str,
        patient_age: int,
        is_pregnant: Optional[bool] = None
    ) -> Optional[dict]:
        """
        Check pregnancy safety.
        
        Returns alert if drug poses pregnancy risk.
        """
        # Only check for women of childbearing age
        if patient_sex.lower() != "female":
            return None
        if patient_age < 15 or patient_age > 55:
            return None
        
        # Category X (contraindicated)
        if drug.pregnancy_category == "X":
            return {
                "severity": "critical",
                "type": "pregnancy",
                "title": "Contraindicated in Pregnancy",
                "message": (
                    f"{drug.name} is pregnancy category X and is "
                    "contraindicated in pregnancy"
                ),
                "recommendation": "Verify pregnancy status before prescribing"
            }
        
        # Category D (evidence of risk)
        if drug.pregnancy_category == "D":
            return {
                "severity": "warning",
                "type": "pregnancy",
                "title": "Pregnancy Category D",
                "message": (
                    f"{drug.name} has positive evidence of fetal risk. "
                    f"{cls.PREGNANCY_CATEGORIES['D']}"
                ),
                "recommendation": "Use only if benefit outweighs risk"
            }
        
        return None
```

## Summary

These domain logic examples show how business rules are:
- **Encapsulated** in dedicated classes
- **Testable** in isolation
- **Documented** with clinical rationale
- **Reusable** across different workflows
- **Consistent** with clinical standards

All of these rules live in **services**, never in BFFs or frontends.
