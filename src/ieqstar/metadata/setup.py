from datetime import datetime, tzinfo
from enum import Enum
from zoneinfo import ZoneInfo

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from . import base, field, sensor, subject


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


class SubjectSensor(BaseModel):
    # Pydantic configuration
    model_config = base.GLOBAL_MODEL_CONFIG

    position: SubjectSensorPosition = Field(
        title='Position',
        description='Sensor position installed on subject (required field)',
        validation_alias=AliasChoices('pos'),
    )

    sensor_info: sensor.SingleSensorBase | sensor.MultiSensorBase = Field(
        title='Sensor info',
        description='Sensor information, as predefined in the SingleSensorBase or MultiSensorBase (required field)',
        discriminator='sensor_type',
    )


class FieldSubject(BaseModel):
    # Pydantic configuration
    model_config = base.GLOBAL_MODEL_CONFIG

    position: str = Field(
        title='Position',
        description='Subject position in field (required field)',
        validation_alias=AliasChoices('pos'),
    )

    subject_info: subject.SubjectBase = Field(
        title='Subject info',
        description='Subject information, as predefined in SubjectBase (required field)',
        validation_alias=AliasChoices('subject info'),
    )

    subject_sensors: dict[str, SubjectSensor] = Field(
        default_factory=dict,
        title='Subject sensors',
        description='Sensors installed on subject, in format {<subject_sensor_id>: SubjectSensor}',
        validation_alias=AliasChoices('subject sensors', 'sensors'),
    )


class FieldSensor(BaseModel):
    # Pydantic configuration
    model_config = base.GLOBAL_MODEL_CONFIG

    position: str = Field(
        title='Position',
        description='Sensor position installed in field (required field)',
        validation_alias=AliasChoices('pos'),
    )

    sensor_info: sensor.SingleSensorBase | sensor.MultiSensorBase = Field(
        title='Sensor info',
        description='Sensor information, as predefined in SingleSensorBase or MultiSensorBase (required field)',
        discriminator='sensor_type',
    )


class SetupField(BaseModel):
    # Pydantic configuration
    model_config = base.GLOBAL_MODEL_CONFIG

    field_info: field.FieldBase = Field(
        title='Field info',
        description='Field information, as predefined in FieldBase (required field)',
        validation_alias=AliasChoices('field info')
    )

    field_subjects: dict[str, FieldSubject] = Field(
        default_factory=dict,
        title='Field subjects',
        description='Subjects in field, in format {<field_subject_id>: FieldSubject}',
        validation_alias=AliasChoices('field subjects', 'subjects'),
    )

    field_sensors: dict[str, FieldSensor] = Field(
        default_factory=dict,
        title='Field sensors',
        description='Sensors in field, in format {<field_sensor_id>: FieldSensor}',
        validation_alias=AliasChoices('field sensors', 'sensors')
    )


class SetupBase(base.MetadataABC):
    # Pydantic configuration
    model_config = ConfigDict(
        **base.MetadataABC.model_config,
        arbitrary_types_allowed=True,
    )

    id_setup: str = Field(
        title='ID setup',
        description='ID to distinguish subject test setups (required field)',
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
        description='Start time of subject test',
        validation_alias=AliasChoices('start time', 't_start'),
        ge=datetime(1900, 1, 1, 0, 0, 0),
        le=datetime.now(),
    )

    end_time: datetime = Field(
        title='End time',
        description='End time of subject test',
        validation_alias=AliasChoices('end time', 't_end'),
        ge=datetime(1900, 1, 1, 0, 0, 0),
        le=datetime.now(),
    )

    @model_validator(mode='after')
    def validate_start_end_time(self) -> 'SetupBase':
        if not self.start_time < self.end_time:
            raise ValueError(f"Start time of setup {self.start_time} must be earlier than end time {self.end_time}")
        return self

    # Setup fields
    setup_fields: dict[str, SetupField] = Field(
        default_factory=dict,
        title='Setup fields',
        description='Subject test setup fields, in format {<setup_field_id>: SetupField}',
        validation_alias=AliasChoices('setup fields', 'fields'),
        min_length=1,
    )
