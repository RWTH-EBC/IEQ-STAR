from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from ieqstar.metadata.field import FieldBase
from ieqstar.metadata.sensor import MultiSensorBase, SingleSensorBase
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
    """Valid data of single-sensor on subject, positioned on the left hand"""
    return {
        'position': 'hand_back_left',
        'sensor_info': SingleSensorBase(**valid_data_sensor_temperature),
    }

@pytest.fixture
def valid_data_subject_sensor_2(valid_data_multi_sensor) -> dict:
    """Valid data of multi-sensor on subject, positioned on the right hand"""
    return {
        'position': 'hand_back_right',
        'sensor_info': MultiSensorBase(**valid_data_multi_sensor)
    }

@pytest.fixture
def valid_data_field_subject(valid_data_subject, valid_data_subject_sensor_1, valid_data_subject_sensor_2) -> dict:
    """Valid data of subject in field, positioned in the front of desk 1, installed with two sensors"""
    return {
        'position': 'desk_1',
        'subject_info': SubjectBase(**valid_data_subject),
        'subject_sensors': {
            'hand_L_Temp': SubjectSensor(**valid_data_subject_sensor_1),
            'hand_R_Temp': SubjectSensor(**valid_data_subject_sensor_2),
        }
    }

@pytest.fixture
def valid_data_field_sensor(valid_data_sensor_co2):
    """Valid data of sensor in field, positioned on the desk 1"""
    return {
        'position': 'desk_1',
        'sensor_info': SingleSensorBase(**valid_data_sensor_co2),
    }

@pytest.fixture
def valid_data_setup_field(valid_data_field, valid_data_field_subject, valid_data_field_sensor) -> dict:
    """Valid data of field for subject test setup, with one subject (installed with two subject sensors) and one field
    sensor in the field"""
    return {
        'field_info': FieldBase(**valid_data_field),
        'field_subjects': {
            'sub_1': FieldSubject(**valid_data_field_subject),
        },
        'field_sensors': {
            'desk_1_CO2': FieldSensor(**valid_data_field_sensor),
        },
    }


@pytest.fixture
def valid_data_setup(valid_data_setup_field) -> dict:
    """Valid data of subject test setup, with one field, in which one subject and one field sensor"""
    return {
        'id_setup': 'Test setup',
        'timezone': 'Europe/Berlin',
        'start_time': '2026-06-01T09:00:00',
        'end_time': '2026-06-01 12:00:00',
        'setup_fields': {
            'room_L': SetupField(**valid_data_setup_field),
        },
    }


class TestSubjectSensorInstantiation:
    """Verify instantiation of SubjectSensor"""
    def test_from_dict(self, valid_data_subject_sensor_1):
        """Instantiation of SubjectSensor from dictionary"""
        subject_sensor = SubjectSensor(**valid_data_subject_sensor_1)
        assert subject_sensor.sensor_info.measurand == "Temperature"  # Confirm inheritance from parent class
        assert subject_sensor.position == SubjectSensorPosition.HAND_BACK_LEFT

    def test_from_json(self, valid_data_subject_sensor_1):
        """Instantiation of SubjectSensor from a JSON string"""
        subject_sensor_from_dict = SubjectSensor(**valid_data_subject_sensor_1)
        json_string = subject_sensor_from_dict.model_dump_json(indent=2)
        subject_sensor_from_json = SubjectSensor.model_validate_json(json_string)
        assert subject_sensor_from_json == subject_sensor_from_dict


class TestFieldSubjectInstantiation:
    """Verify instantiation of FieldSubject"""
    def test_from_dict(self, valid_data_field_subject, valid_data_subject_sensor_1):
        """Instantiation of FieldSubject from dictionary"""
        field_subject = FieldSubject(**valid_data_field_subject)
        assert field_subject.subject_info.last_name == "Mustermann"  # Confirm inheritance from parent class
        assert field_subject.position == "desk_1"
        assert field_subject.subject_sensors['hand_L_Temp'] == SubjectSensor(**valid_data_subject_sensor_1)

    def test_from_json(self, valid_data_field_subject):
        """Instantiation of FieldSubject from a JSON string"""
        field_subject_from_dict = FieldSubject(**valid_data_field_subject)
        json_string = field_subject_from_dict.model_dump_json(indent=2)
        field_subject_from_json = FieldSubject.model_validate_json(json_string)
        assert field_subject_from_json == field_subject_from_dict


class TestFieldSensorInstantiation:
    """Verify instantiation of FieldSensor"""
    def test_from_dict(self, valid_data_field_sensor):
        """Instantiation of FieldSensor from dictionary"""
        field_sensor = FieldSensor(**valid_data_field_sensor)
        assert field_sensor.sensor_info.measurand == "CO2 concentration"  # Confirm inheritance from parent class
        assert field_sensor.position == "desk_1"

    def test_from_json(self, valid_data_field_sensor):
        """Instantiation of FieldSensor from a JSON string"""
        field_sensor_from_dict = FieldSensor(**valid_data_field_sensor)
        json_string = field_sensor_from_dict.model_dump_json(indent=2)
        field_sensor_from_json = FieldSensor.model_validate_json(json_string)
        assert field_sensor_from_json == field_sensor_from_dict


class TestSetupFieldInstantiation:
    """Verify instantiation of SetupField"""
    def test_from_dict(self, valid_data_setup_field):
        """Instantiation of SetupField from dictionary"""
        setup_field = SetupField(**valid_data_setup_field)
        assert setup_field.field_info.length == 2.0  # Confirm inheritance from parent class
        assert setup_field.field_subjects['sub_1'].subject_info.last_name == "Mustermann"
        assert setup_field.field_sensors['desk_1_CO2'].sensor_info.measurand == "CO2 concentration"

    def test_from_json(self, valid_data_setup_field):
        """Instantiation of SetupField from a JSON string"""
        setup_field_from_dict = SetupField(**valid_data_setup_field)
        json_string = setup_field_from_dict.model_dump_json(indent=2)
        setup_field_from_json = SetupField.model_validate_json(json_string)
        assert setup_field_from_json == setup_field_from_dict


class TestSetupInstantiation:
    """Verify instantiation of SetupBase"""
    def test_from_dict(self, valid_data_setup):
        """Instantiation of SetupBase from dictionary"""
        setup = SetupBase(**valid_data_setup)
        assert setup.id_setup == "Test setup"
        assert setup.timezone == ZoneInfo("Europe/Berlin")
        assert setup.start_time == datetime(2026, 6, 1, 9, 0, 0)
        assert setup.end_time == datetime(2026, 6, 1, 12, 0, 0)  # Confirm different input format of datetime
        assert len(setup.setup_fields['room_L'].field_subjects) == 1
        assert len(setup.setup_fields['room_L'].field_sensors) == 1
        assert len(setup.setup_fields['room_L'].field_subjects['sub_1'].subject_sensors) == 2

    def test_from_json(self, valid_data_setup):
        """Instantiation of SetupBase from a JSON string"""
        setup_from_dict = SetupBase(**valid_data_setup)
        json_string = setup_from_dict.model_dump_json(indent=2)
        setup_from_json = SetupBase.model_validate_json(json_string)
        assert setup_from_json == setup_from_dict
