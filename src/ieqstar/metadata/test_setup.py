from datetime import datetime, tzinfo
from enum import Enum
from zoneinfo import ZoneInfo

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from . import field, sensor, subject


class SubjectSensorPosition(str, Enum):
    """Position for sensor installation on subject"""
    FOREHEAD = 'forehead'
    NECK = 'neck'

    COLLARBONE_BELOW = 'collarbone_below'
    SCAPULA = 'scapula'
    NAVEL_BESIDE = 'navel_beside'
    LUMBAR_REGION = 'lumbar_region'

    UPPER_ARM_LEFT = 'upper_arm_left'
    UPPER_ARM_RIGHT = 'upper_arm_right'
    LOWER_ARM_LEFT = 'lower_arm_left'
    LOWER_ARM_RIGHT = 'lower_arm_right'
    HAND_BACK_LEFT = 'hand_back_left'
    HAND_BACK_RIGHT = 'hand_back_right'

    POSTERIOR = 'posterior'

    THIGH_FRONT_LEFT = 'thigh_front_left'
    THIGH_FRONT_RIGHT = 'thigh_front_right'
    THIGH_BACK_LEFT = 'thigh_back_left'
    THIGH_BACK_RIGHT = 'thigh_back_right'
    SHIN_LEFT = 'shin_left'
    SHIN_RIGHT = 'shin_right'
    CALF_LEFT = 'calf_left'
    CALF_RIGHT = 'calf_right'
    INSTEP_LEFT = 'instep_left'
    INSTEP_RIGHT = 'instep_right'
    FOOT_BOTTOM_LEFT = 'foot_bottom_left'
    FOOT_BOTTOM_RIGHT = 'foot_bottom_right'


class SubjectSensor(sensor.SensorBase):
    id_setup: str = Field(
        title='ID in test setup',
        description='ID to distinguish sensors on subject for test setup (required field)',
        validation_alias=AliasChoices('ID setup', 'ID'),
        min_length=1,
    )

    position: SubjectSensorPosition = Field(
        title='Position',
        description='Sensor position installed on subject (required field)',
        validation_alias=AliasChoices('pos'),
    )

    @classmethod
    def from_sensor_base(
            cls,
            sensor_base: sensor.SensorBase,
            id_setup: str,
            position: SubjectSensorPosition
    ):
        """Create SubjectSensor from SensorBase"""
        return cls(
            **sensor_base.model_dump(),
            id_setup=id_setup,
            position=position,
        )


class TestSubject(subject.SubjectBase):
    id_setup: str = Field(
        title='ID in test setup',
        description='ID to distinguish subjects in field for test setup (required field)',
        validation_alias=AliasChoices('ID setup', 'ID'),
        min_length=1,
    )

    position: str = Field(
        title='Position',
        description='Subject position in field',
        validation_alias=AliasChoices('pos'),
    )

    subject_sensors: list[SubjectSensor] = Field(
        default_factory=list,
        title='Subject sensors',
        description='Sensors installed on subject',
        validation_alias=AliasChoices('subject sensors', 'sensors'),
    )

    @classmethod
    def from_subject_base(
            cls,
            subject_base: subject.SubjectBase,
            id_setup: str,
            position: str,
            subject_sensors: list[SubjectSensor] | None = None,
    ):
        """Create TestSubject from SubjectBase"""
        return cls(
            **subject_base.model_dump(),
            id_setup=id_setup,
            position=position,
            subject_sensors=subject_sensors or [],
        )


class FieldSensor(sensor.SensorBase):
    id_setup: str = Field(
        title='ID in test setup',
        description='ID to distinguish sensors in field for test setup (required field)',
        validation_alias=AliasChoices('ID setup', 'ID'),
        min_length=1,
    )

    position: str = Field(
        title='Position',
        description='Sensor position in field',
        validation_alias=AliasChoices('pos'),
    )

    @classmethod
    def from_sensor_base(
            cls,
            sensor_base: sensor.SensorBase,
            id_setup: str,
            position: str
    ):
        """Create FieldSensor from SensorBase"""
        return cls(
            **sensor_base.model_dump(),
            id_setup=id_setup,
            position=position,
        )


class TestField(field.FieldBase):
    id_setup: str = Field(
        title='ID in test setup',
        description='ID to distinguish fields for test setup (required field)',
    )

    test_subjects: list[TestSubject] = Field(
        default_factory=list,
        title='Test subjects',
        description='Test subjects in field',
        validation_alias=AliasChoices('test subjects', 'subjects'),
    )

    field_sensors: list[FieldSensor] = Field(
        default_factory=list,
        title='Field sensors',
        description='Field sensors in field',
        validation_alias=AliasChoices('field sensors', 'sensors')
    )

    @classmethod
    def from_field_base(
            cls,
            field_base: field.FieldBase,
            test_subjects: list[TestSubject] | None = None,
            field_sensors: list[FieldSensor] | None = None,
    ):
        """Create TestField from FieldBase"""
        return cls(
            **field_base.model_dump(),
            test_subjects=test_subjects or [],
            field_sensors=field_sensors or [],
        )


class TestSetupBase(BaseModel):
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id_setup: str = Field(
        title='ID in test setup',
        description='ID to distinguish test setups (required field)',
        validation_alias=AliasChoices('ID setup', 'ID'),
    )

    # Time
    timezone: tzinfo = Field(
        title='Timezone',
        description='Timezone of start and end times',
        validation_alias=AliasChoices('tz'),
    )

    @field_validator('timezone', mode='before')
    @classmethod
    def timezone_from_str(cls, tz: str | tzinfo) -> tzinfo:
        if isinstance(tz, str):
            return ZoneInfo(tz)
        elif isinstance(tz, tzinfo):
            return tz
        else:
            raise ValueError(f"Invalid time zone '{tz}', it must be string or datetime.tzinfo")

    @field_serializer('timezone', mode='plain')
    def timezone_to_str(self, tz: tzinfo) -> str:
        if hasattr(tz, 'key'):
            return tz.key
        else:
            return str(tz)

    start_time: datetime = Field(
        title='Start time',
        description='Start time of test',
        validation_alias=AliasChoices('start time', 't_start'),
        ge=datetime(1900, 1, 1, 0, 0, 0),
        le=datetime.now(),
    )

    end_time: datetime = Field(
        title='End time',
        description='End time of test',
        validation_alias=AliasChoices('end time', 't_end'),
        ge=datetime(1900, 1, 1, 0, 0, 0),
        le=datetime.now(),
    )

    @model_validator(mode='after')
    def validate_start_end_time(self) -> 'TestSetupBase':
        if self.start_time >= self.end_time:
            raise ValueError(f"Start time of test {self.start_time} must be earlier than end time {self.end_time}")
        return self

    # Test fields
    test_fields: list[TestField] = Field(
        default_factory=list,
        title='Test fields',
        description='Test fields, which consist of test subjects and field sensors',
        validation_alias=AliasChoices('test fields', 'fields'),
        min_length=1,
    )
