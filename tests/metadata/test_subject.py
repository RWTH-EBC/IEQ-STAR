from datetime import date, timedelta
import json
import pytest
from pydantic import ValidationError
from ieqstar.metadata.subject import SubjectBase, Gender


class TestInstantiation:
    """Verify instantiation of SubjectBase"""
    def test_from_dict(self, valid_data_subject):
        """Instantiation of SubjectBase from a dictionary"""
        subject = SubjectBase(**valid_data_subject)
        assert subject.last_name_at_birth == "Mustermann"
        assert subject.last_name == "Mustermann"  # Confirm default value set as last_name_of_birth
        assert subject.first_name == "Max"
        assert subject.middle_name == "Maria"
        assert subject.birth_date == date(1992, 5, 20)
        assert subject.gender == Gender.MALE
        assert subject.registration_date == date.today()
        assert subject.height_logs[0].height == 1.79  # Confirm rounding to 2 decimals
        assert subject.height_logs[-1].log_date == date(2026, 3, 1)  # Confirm date sorted in ascending sequence
        assert subject.weight_logs[0].weight == 67.9  # Confirm rounding to 1 decimal
        assert subject.weight_logs[-1].log_date == date(2026, 3, 1)  # Confirm date sorted in ascending sequence
        assert subject.phone == "tel:+49-176-12345678"
        assert subject.email == "max.mustermann@sub-domain.domain.de"
        assert subject.registration_date == date.today()  # Confirm default date is today

    def test_from_json(self, valid_data_subject):
        """Instantiation of SubjectBase from a JSON string"""
        subject_from_dict = SubjectBase(**valid_data_subject)
        json_string = json.dumps(valid_data_subject)
        subject_from_json = SubjectBase.model_validate_json(json_string)
        assert subject_from_json == subject_from_dict

    def test_defined_last_name(self, valid_data_subject):
        """Test defined last name as it differs from last name at birth"""
        valid_data_subject['last_name'] = "Musterfrau"
        subject = SubjectBase(**valid_data_subject)
        assert subject.last_name_at_birth == "Mustermann"
        assert subject.last_name == "Musterfrau"


class TestNameRegexPatterns:
    """Verify name regex behavior"""
    @pytest.mark.parametrize(
        "name",
        ["Álvaro", "Müller", "Smith Brown", "Smith-Brown", "O'Connor"]
    )
    def test_valid(self, valid_data_subject, name):
        """Validate international unicode-compliant name variations"""
        valid_data_subject['last_name_at_birth'] = name
        subject = SubjectBase(**valid_data_subject)
        assert subject.last_name == name

    @pytest.mark.parametrize(
        "name",
        ["Smith123", "Smith  Brown", "Smith-", " Smith", "O' Connor"]
    )
    def test_invalid(self, valid_data_subject, name):
        """Ensure structural name violations trigger validation errors"""
        valid_data_subject['last_name_at_birth'] = name
        with pytest.raises(ValidationError):
            SubjectBase(**valid_data_subject)


def test_unique_dates_validator(valid_data_subject):
    """Confirm duplicate logging dates fail custom array validations"""
    valid_data_subject['height_logs'] = [
        {'log_date': '2026-03-01' , 'height': 1.75},
        {'log_date': '2026-03-01' , 'height': 1.85},  # Duplicate log_date
    ]
    with pytest.raises(ValidationError) as e:
        SubjectBase(**valid_data_subject)
    assert "Duplicated log entry" in str(e.value)


def test_future_dates_blocked(valid_data_subject):
    """Ensure date of birth cannot accidentally sit in the future"""
    tomorrow = date.today() + timedelta(days=1)
    valid_data_subject['birth_date'] = tomorrow.strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        SubjectBase(**valid_data_subject)


@pytest.mark.parametrize(
    "first_name, last_name_at_birth, expected_pii",
    [
        ('Max', 'Mustermann' , 'max|mustermann|1992-05-20|m'),
        ('Hans-Peter', 'Müller-Maier', 'hanspeter|müllermaier|1992-05-20|m')
    ]
)
def test_computed_fields_and_id_generation(valid_data_subject, first_name, last_name_at_birth, expected_pii):
    """Check predictability of generated internal cryptographic PII tokens."""
    valid_data_subject['first_name'] = first_name
    valid_data_subject['last_name_at_birth'] = last_name_at_birth
    subject = SubjectBase(**valid_data_subject)
    assert subject.pii == expected_pii
    assert len(subject.id_full) == 64
    assert len(subject.id_short) == 8
    assert subject.id_full.startswith(subject.id_short)


def test_frozen_fields(valid_data_subject):
    """Ensure identity immutability settings block accidental runtime edits."""
    subject = SubjectBase(**valid_data_subject)
    with pytest.raises(ValidationError):
        subject.first_name = "Alexander"
