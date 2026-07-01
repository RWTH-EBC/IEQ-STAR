import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from ieqstar.metadata.field import FieldBase
from ieqstar.metadata.sensor import SensorBase
from ieqstar.metadata.setup import (
    FieldSensor,
    FieldSubject,
    SetupBase,
    SetupField,
    SubjectSensor,
    SubjectSensorPosition,
)
from ieqstar.metadata.subject import SubjectBase


@pytest.fixture
def valid_data_subject_sensor_1(valid_data_sensor_temperature) -> dict:
    """Valid data of sensor on subject, positioned on the left hand"""
    return {
        **valid_data_sensor_temperature,
        'id_setup': 'sen_T_hand_L',
        'position': 'hand_back_left',
    }

@pytest.fixture
def valid_data_subject_sensor_2(valid_data_sensor_temperature) -> dict:
    """Valid data of sensor on subject, positioned on the right hand"""
    return {
        **valid_data_sensor_temperature,
        'id_setup': 'sen_T_hand_R',
        'position': 'hand_back_right',
    }

@pytest.fixture
def valid_data_field_subject(valid_data_subject, valid_data_subject_sensor_1, valid_data_subject_sensor_2) -> dict:
    """Valid data of subject in field, positioned in the left test chamber, installed with two sensors"""
    return {
        **valid_data_subject,
        'id_setup': 'sub_1',
        'position': 'chamber_L',
        'subject_sensors': [
            {**valid_data_subject_sensor_1},
            {**valid_data_subject_sensor_2},
        ],
    }

@pytest.fixture
def valid_data_field_sensor(valid_data_sensor_co2):
    """Valid data of sensor in field, positioned in the left test chamber"""
    return {
        **valid_data_sensor_co2,
        'id_setup': 'sen_CO2_chamber_L',
        'position': 'chamber_L',
    }

@pytest.fixture
def valid_data_setup_field(valid_data_field, valid_data_field_subject, valid_data_field_sensor) -> dict:
    """Valid data of field (left test chamber) for subject test setup, with one subject (installed with two subject
    sensors) and one field sensor in the field"""
    return {
        **valid_data_field,
        'id_setup': 'chamber_L',
        'field_subjects': [
            {**valid_data_field_subject},
        ],
        'field_sensors': [
            {**valid_data_field_sensor},
        ],
    }


@pytest.fixture
def valid_data_setup(valid_data_setup_field) -> dict:
    """Valid data of subject test setup, with one field, in which one subject and one field sensor"""
    return {
        'id_setup': 'Test setup',
        'timezone': 'Europe/Berlin',
        'start_time': '2026-06-01T09:00:00',
        'end_time': '2026-06-01 12:00:00',
        'setup_fields': [{**valid_data_setup_field}],
    }


class TestSubjectSensorInstantiation:
    """Verify instantiation of SubjectSensor"""
    def test_from_dict(self, valid_data_subject_sensor_1):
        """Instantiation of SubjectSensor from dictionary"""
        subject_sensor = SubjectSensor(**valid_data_subject_sensor_1)
        assert subject_sensor.measurand == "Temperature"  # Confirm inheritance from parent class
        assert subject_sensor.id_setup == "sen_T_hand_L"
        assert subject_sensor.position == SubjectSensorPosition.HAND_BACK_LEFT

    def test_from_json(self, valid_data_subject_sensor_1):
        """Instantiation of SubjectSensor from a JSON string"""
        subject_sensor_from_dict = SubjectSensor(**valid_data_subject_sensor_1)
        json_string = json.dumps(valid_data_subject_sensor_1)
        subject_sensor_from_json = SubjectSensor.model_validate_json(json_string)
        assert subject_sensor_from_dict == subject_sensor_from_json

    def test_from_class_method(self, valid_data_subject_sensor_1, valid_data_sensor_temperature):
        """Instantiation of SubjectSensor from class method"""
        subject_sensor_from_dict = SubjectSensor(**valid_data_subject_sensor_1)
        subject_sensor_from_class_method = SubjectSensor.from_sensor_base(
            sensor_base=SensorBase(**valid_data_sensor_temperature),
            id_setup=valid_data_subject_sensor_1['id_setup'],
            position=valid_data_subject_sensor_1['position'],
        )
        assert subject_sensor_from_dict == subject_sensor_from_class_method


class TestFieldSubjectInstantiation:
    """Verify instantiation of FieldSubject"""
    def test_from_dict(self, valid_data_field_subject, valid_data_subject_sensor_1):
        """Instantiation of FieldSubject from dictionary"""
        field_subject = FieldSubject(**valid_data_field_subject)
        assert field_subject.last_name == "Mustermann"  # Confirm inheritance from parent class
        assert field_subject.id_setup == "sub_1"
        assert field_subject.position == "chamber_L"
        assert field_subject.subject_sensors[0] == SubjectSensor(**valid_data_subject_sensor_1)

    def test_from_json(self, valid_data_field_subject):
        """Instantiation of FieldSubject from a JSON string"""
        field_subject_from_dict = FieldSubject(**valid_data_field_subject)
        json_string = json.dumps(valid_data_field_subject)
        field_subject_from_json = FieldSubject.model_validate_json(json_string)
        assert field_subject_from_dict == field_subject_from_json

    def test_from_class_method(
            self,
            valid_data_field_subject,
            valid_data_subject,
            valid_data_subject_sensor_1,
            valid_data_subject_sensor_2
    ):
        """Instantiation of FieldSubject from class method"""
        field_subject_from_dict = FieldSubject(**valid_data_field_subject)
        field_subject_from_class_method = FieldSubject.from_subject_base(
            subject_base=SubjectBase(**valid_data_subject),
            id_setup=valid_data_field_subject['id_setup'],
            position=valid_data_field_subject['position'],
            subject_sensors=[
                SubjectSensor(**valid_data_subject_sensor_1),
                SubjectSensor(**valid_data_subject_sensor_2),
            ],
        )
        assert field_subject_from_dict == field_subject_from_class_method


class TestFieldSensorInstantiation:
    """Verify instantiation of FieldSensor"""
    def test_from_dict(self, valid_data_field_sensor):
        """Instantiation of FieldSensor from dictionary"""
        field_sensor = FieldSensor(**valid_data_field_sensor)
        assert field_sensor.measurand == "CO2"  # Confirm inheritance from parent class
        assert field_sensor.id_setup == "sen_CO2_chamber_L"
        assert field_sensor.position == "chamber_L"

    def test_from_json(self, valid_data_field_sensor):
        """Instantiation of FieldSensor from a JSON string"""
        field_sensor_from_dict = FieldSensor(**valid_data_field_sensor)
        json_string = json.dumps(valid_data_field_sensor)
        field_sensor_from_json = FieldSensor.model_validate_json(json_string)
        assert field_sensor_from_dict == field_sensor_from_json

    def test_from_class_method(self, valid_data_field_sensor, valid_data_sensor_co2):
        """Instantiation of FieldSensor from class method"""
        field_sensor_from_dict = FieldSensor(**valid_data_field_sensor)
        field_sensor_from_class_method = FieldSensor.from_sensor_base(
            sensor_base=SensorBase(**valid_data_sensor_co2),
            id_setup=valid_data_field_sensor['id_setup'],
            position=valid_data_field_sensor['position'],
        )
        assert field_sensor_from_dict == field_sensor_from_class_method


class TestSetupFieldInstantiation:
    """Verify instantiation of SetupField"""
    def test_from_dict(self, valid_data_setup_field):
        """Instantiation of SetupField from dictionary"""
        setup_field = SetupField(**valid_data_setup_field)
        assert setup_field.length == pytest.approx(2.0)  # Confirm inheritance from parent class
        assert setup_field.id_setup == "chamber_L"
        assert setup_field.field_subjects[0].last_name == "Mustermann"
        assert setup_field.field_sensors[0].measurand == "CO2"

    def test_from_json(self, valid_data_setup_field):
        """Instantiation of SetupField from a JSON string"""
        setup_field_from_dict = SetupField(**valid_data_setup_field)
        json_string = json.dumps(valid_data_setup_field)
        setup_field_from_json = SetupField.model_validate_json(json_string)
        assert setup_field_from_dict == setup_field_from_json

    def test_from_class_method(
            self,
            valid_data_setup_field,
            valid_data_field,
            valid_data_field_subject,
            valid_data_field_sensor,
    ):
        """Instantiation of SetupField from class method"""
        setup_field_from_dict = SetupField(**valid_data_setup_field)
        setup_field_from_class_method = SetupField.from_field_base(
            field_base=FieldBase(**valid_data_field),
            id_setup=valid_data_setup_field['id_setup'],
            field_subjects=[FieldSubject(**valid_data_field_subject)],
            field_sensors=[FieldSensor(**valid_data_field_sensor)],
        )
        assert setup_field_from_dict == setup_field_from_class_method


class TestSetupInstantiation:
    """Verify instantiation of SetupBase"""
    def test_from_dict(self, valid_data_setup):
        """Instantiation of SetupBase from dictionary"""
        setup = SetupBase(**valid_data_setup)
        assert setup.id_setup == "Test setup"
        assert setup.timezone == ZoneInfo("Europe/Berlin")
        assert setup.start_time == datetime(2026, 6, 1, 9, 0, 0)
        assert setup.end_time == datetime(2026, 6, 1, 12, 0, 0)  # Confirm different input format of datetime
        assert setup.setup_fields[0].id_setup == "chamber_L"
        assert len(setup.setup_fields[0].field_subjects) == 1
        assert len(setup.setup_fields[0].field_sensors) == 1
        assert len(setup.setup_fields[0].field_subjects[0].subject_sensors) == 2

    def test_from_json(self, valid_data_setup):
        """Instantiation of SetupBase from a JSON string"""
        setup_from_dict = SetupBase(**valid_data_setup)
        json_string = json.dumps(valid_data_setup)
        setup_from_json = SetupBase.model_validate_json(json_string)
        assert setup_from_dict == setup_from_json
