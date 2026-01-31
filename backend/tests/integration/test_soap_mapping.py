"""
Integration tests for SOAP mapping endpoint.

Tests the POST /encounters/{encounter_id}/soap-mapping endpoint which parses
clinical note content into structured SOAP sections.
"""

import asyncio
import pytest

from tests.integration.conftest import TestPatients, TestProviders


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def create_test_encounter(client) -> str:
    """Create a test encounter and return its ID."""
    response = client.post(
        f"/patients/{TestPatients.SARAH_JOHNSON['id']}/encounters",
        json={
            "patientId": TestPatients.SARAH_JOHNSON["id"],
            "providerId": TestProviders.DR_FROST["id"],
            "encounterType": "office-visit",
            "chiefComplaint": "Test visit",
        },
    )
    assert response.status_code == 200
    return response.json()["encounter"]["id"]


class TestSOAPMappingEndpoint:
    """Tests for the SOAP mapping API endpoint."""

    def test_soap_mapping_with_explicit_markers(self, client):
        """Test parsing note with explicit SOAP section markers."""
        encounter_id = create_test_encounter(client)

        note_content = """
Subjective:
Patient is a 45-year-old male presenting with complaints of persistent headache
for the past 3 days. He describes the pain as throbbing, located in the frontal
region, rated 6/10 in severity. Patient reports associated photophobia and
mild nausea but denies vomiting, fever, or neck stiffness.

Objective:
Vitals: BP 138/88, HR 78, Temp 98.6F, RR 16
General: Alert and oriented, in no acute distress
HEENT: Pupils equal and reactive, no papilledema on fundoscopic exam
Neck: Supple, no meningismus

Assessment:
1. Tension-type headache, likely stress-related
2. Mild hypertension - likely white coat effect
Patient's presentation is most consistent with tension headache given the
bilateral location and lack of neurological deficits.

Plan:
1. Start acetaminophen 500mg every 6 hours as needed for headache
2. Encourage adequate hydration and regular sleep schedule
3. Stress management techniques discussed
4. Follow up in 2 weeks if symptoms persist
5. Return precautions given for worsening symptoms
"""

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": note_content},
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "subjective" in data
        assert "objective" in data
        assert "assessment" in data
        assert "plan" in data
        assert "overallCompleteness" in data

        # Check each section has expected fields
        for section in ["subjective", "objective", "assessment", "plan"]:
            assert "content" in data[section]
            assert "completeness" in data[section]
            assert "wordCount" in data[section]

        # All sections should have content
        assert data["subjective"]["wordCount"] > 0
        assert data["objective"]["wordCount"] > 0
        assert data["assessment"]["wordCount"] > 0
        assert data["plan"]["wordCount"] > 0

        # Overall should be complete or partial since all sections have content
        assert data["overallCompleteness"] in ["complete", "partial"]

    def test_soap_mapping_empty_content(self, client):
        """Test parsing empty note content."""
        encounter_id = create_test_encounter(client)

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": ""},
        )

        assert response.status_code == 200
        data = response.json()

        # All sections should be empty
        for section in ["subjective", "objective", "assessment", "plan"]:
            assert data[section]["content"] == ""
            assert data[section]["completeness"] == "empty"
            assert data[section]["wordCount"] == 0

        assert data["overallCompleteness"] == "empty"

    def test_soap_mapping_partial_note(self, client):
        """Test parsing note with only some sections."""
        encounter_id = create_test_encounter(client)

        note_content = """
Subjective:
Patient reports feeling tired for the past week.

Plan:
Rest and hydration recommended.
"""

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": note_content},
        )

        assert response.status_code == 200
        data = response.json()

        # Subjective and Plan should have content
        assert data["subjective"]["wordCount"] > 0
        assert data["plan"]["wordCount"] > 0

        # Objective and Assessment should be empty
        assert data["objective"]["completeness"] == "empty"
        assert data["assessment"]["completeness"] == "empty"

        # Overall should be partial
        assert data["overallCompleteness"] == "partial"

    def test_soap_mapping_alternative_markers(self, client):
        """Test parsing note with alternative section markers (S:, O:, A:, P:)."""
        encounter_id = create_test_encounter(client)

        note_content = """
S: Patient complains of sore throat for two days, difficulty swallowing.

O: Pharynx erythematous with tonsillar enlargement bilaterally.
Temp 100.4F. Tender anterior cervical lymphadenopathy.

A: Acute pharyngitis, likely viral vs streptococcal.

P: Rapid strep test ordered. Supportive care. Return if worsening.
"""

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": note_content},
        )

        assert response.status_code == 200
        data = response.json()

        # All sections should have content
        assert data["subjective"]["wordCount"] > 0
        assert data["objective"]["wordCount"] > 0
        assert data["assessment"]["wordCount"] > 0
        assert data["plan"]["wordCount"] > 0

    def test_soap_mapping_encounter_not_found(self, client):
        """Test error handling for non-existent encounter."""
        response = client.post(
            "/encounters/non-existent-id/soap-mapping",
            json={"content": "Some note content"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_soap_mapping_hpi_marker(self, client):
        """Test parsing note using HPI marker for subjective."""
        encounter_id = create_test_encounter(client)

        note_content = """
HPI:
The patient is a 55-year-old female with history of diabetes presenting
with increased thirst and urination over the past two weeks.

Physical Exam:
General: Well-appearing, no acute distress
Skin: Dry mucous membranes

Assessment:
Poorly controlled diabetes mellitus

Treatment Plan:
Increase metformin dose and recheck A1C in 3 months.
"""

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": note_content},
        )

        assert response.status_code == 200
        data = response.json()

        # HPI should map to subjective
        assert data["subjective"]["wordCount"] > 0
        assert "diabetes" in data["subjective"]["content"].lower()

    def test_soap_mapping_completeness_thresholds(self, client):
        """Test completeness calculation based on word count thresholds."""
        encounter_id = create_test_encounter(client)

        # Note with varying section lengths
        note_content = """
Subjective:
Brief complaint.

Objective:
Normal exam findings. Blood pressure is 120/80 mmHg. Heart rate is 72 bpm.
Temperature is normal at 98.6 degrees. Respiratory rate is 16 per minute.
Patient appears well nourished and in no acute distress.

Assessment:
The patient has a mild upper respiratory infection with associated symptoms
of nasal congestion, mild cough, and low grade fever. No signs of bacterial
infection at this time. Lungs are clear bilaterally with good air movement.
This appears to be a self-limiting viral illness that should resolve with
supportive care over the next several days.

Plan:
Rest.
"""

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": note_content},
        )

        assert response.status_code == 200
        data = response.json()

        # Subjective: 2 words = partial
        assert data["subjective"]["completeness"] == "partial"

        # Objective: ~40 words = complete
        assert data["objective"]["completeness"] == "complete"

        # Assessment: ~60 words = complete
        assert data["assessment"]["completeness"] == "complete"

        # Plan: 1 word = partial
        assert data["plan"]["completeness"] == "partial"

    def test_soap_mapping_inferred_sections(self, client):
        """Test parsing unstructured note by inferring sections."""
        encounter_id = create_test_encounter(client)

        # Note without explicit SOAP markers
        note_content = """
Patient reports persistent lower back pain for 3 weeks after lifting heavy boxes.
Pain is worse with bending and improves with rest.
Patient denies numbness or tingling in legs.

BP: 128/82, HR: 76, Temp: 98.4F
On exam, patient has tenderness to palpation of lumbar paraspinal muscles.
No neurological deficits noted.
Range of motion limited by pain.

Likely mechanical low back pain.
Rule out disc herniation if symptoms worsen.

Start ibuprofen 400mg three times daily.
Physical therapy referral.
Follow up in 2 weeks.
"""

        response = client.post(
            f"/encounters/{encounter_id}/soap-mapping",
            json={"content": note_content},
        )

        assert response.status_code == 200
        data = response.json()

        # At minimum, the parser should categorize some content
        total_words = sum(
            data[section]["wordCount"]
            for section in ["subjective", "objective", "assessment", "plan"]
        )

        # Some content should be mapped
        assert total_words > 0
