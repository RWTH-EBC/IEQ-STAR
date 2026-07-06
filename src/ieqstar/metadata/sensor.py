from abc import ABC
from datetime import date
from enum import Enum
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, field_serializer, field_validator, model_validator

from . import base


class SensorAccuracyErrorCombination(str, Enum):
    """Combinations of absolute and relative errors for sensor accuracy calculation"""
    ADD = 'add'  # Add values of absolute and relative errors
    MAX = 'max'  # Max value of absolute and relative errors


class SensorAccuracyByRange(BaseModel):
    """Sensor accuracy by a specific range"""
    # Pydantic configuration
    model_config = base.GLOBAL_MODEL_CONFIG

    absolute_error: float = Field(
        default=0.0,
        title='Absolute error',
        description='Absolute error (required field), fixed absolute error, e.g. 0.1 for +/-0.1',
        validation_alias=AliasChoices('abs err', 'abs'),
        ge=0.0,
    )

    relative_error: float = Field(
        default=0.0,
        title='Relative error',
        description='Relative error (required field), relative error regarding measured value, e.g. 0.05 for 5 % of '
                    'the measured value (mv)',
        validation_alias=AliasChoices('rel err', 'rel'),
        ge=0.0,
    )

    error_combination: SensorAccuracyErrorCombination = Field(
        default=SensorAccuracyErrorCombination.ADD,
        title='Error combination',
        description='Combination of absolute and relative errors for sensor accuracy calculation (required field)',
        validation_alias=AliasChoices('error combination', 'error comb', 'err comb'),
    )

    def calculate_error(self, measured_value: float) -> float:
        if self.error_combination == SensorAccuracyErrorCombination.ADD:
            return self.absolute_error + self.relative_error * abs(measured_value)
        if self.error_combination == SensorAccuracyErrorCombination.MAX:
            return max(self.absolute_error, self.relative_error * abs(measured_value))
        raise ValueError(f"Error combination {self.error_combination} not implemented")


class SensorABC(base.MetadataABC, ABC):
    """ABC for SensorBase and MultiSensorBase"""
    # Discriminator
    sensor_type: str

    # Manufacture
    manufacturer: str = Field(
        title='Manufacturer',
        description='Manufacturer (required field)',
        validation_alias=AliasChoices('mfr.', 'mfr'),
        min_length=1,
        max_length=50,
    )

    model_name: str | None = Field(
        default=None,
        title='Model',
        description='Model type, which describes the general characteristics and technical specifications shared by an '
                    'entire batch or line of products',
        validation_alias=AliasChoices(
            'model name', 'model', 'type', 'type code', 'module', 'module type', 'part number', 'P/N', 'PN'
        ),
        min_length=1,
        max_length=50,
    )

    serial_number: str | None = Field(
        default=None,
        title='Serial number',
        description='Serial number, which is a completely unique identifier assigned to one specific product',
        validation_alias=AliasChoices('serial number', 'S/N', 'SN'),
        min_length=1,
        max_length=50,
    )


class SingleSensorBase(SensorABC):
    """Single sensor or transducer"""
    # Discriminator
    sensor_type: Literal['single'] = 'single'

    # Measurement
    measurand: str = Field(
        title='Measurand',
        description='Measurand (required field), defined as the physical quantity that the sensor intends to measure',
        # Ref: https://www.sciencedirect.com/topics/engineering/measurand
        validation_alias=AliasChoices('parameter', 'variable', 'value'),
        min_length=1,
        max_length=50,
    )

    unit: str = Field(
        title='Unit',
        description='Measurement unit (required field)',
        min_length=1,
        max_length=20,
    )

    range: tuple[float, float] = Field(
        title='Range',
        description='Measurement range of the sensor (required field), in (min, max)',
    )

    # Validate range
    @field_validator('range')
    @classmethod
    def validate_range(cls, rg: tuple[float, float]) -> tuple[float, float]:
        """Ensure minimum is less than maximum range"""
        if not rg[0] < rg[1]:
            raise ValueError(
                f"Minimum range value {rg[0]} of sensor must be strictly less than maximum range value {rg[1]}"
            )
        return rg

    resolution: float = Field(
        title='Resolution',
        description='Measurement resolution (required field)',
        gt=0,
    )

    accuracies: dict[tuple[float, float], SensorAccuracyByRange] = Field(
        default_factory=dict,
        title='Accuracies',
        description='Measurement accuracies by various ranges (required field), in format '
                    '{<(range_min, range_max)>: <SensorAccuracyByRange>}',
        min_length=1,
    )

    @field_validator('accuracies', mode='before')
    @classmethod
    def accuracies_key_from_str(
            cls,
            accs: dict[str, SensorAccuracyByRange] | dict[tuple[float, float], SensorAccuracyByRange]
    ) -> dict[tuple[float, float], SensorAccuracyByRange]:
        accs_output = {}
        for k, v in accs.items():
            if isinstance(k, tuple):
                accs_output[k] = v
            elif isinstance(k, str):
                rg_min_str, rg_max_str = k.strip().replace('(', '').replace(')', '').split(',')
                accs_output[(float(rg_min_str.strip()), float(rg_max_str.strip()))] = v
            else:
                raise ValueError(
                    f"Invalid accuracy key {k}, it must be tuple or string of tuple in format tuple[float, float]"
                )
        return accs_output

    @field_serializer('accuracies', mode='plain')
    def accuracies_key_to_str(
            self, accs: dict[tuple[float, float], SensorAccuracyByRange]
    ) -> dict[str, SensorAccuracyByRange]:
        return {str(k): v for k, v in accs.items()}

    @field_validator('accuracies')
    @classmethod
    def validate_accuracies_range(
            cls, accs: dict[tuple[float, float], SensorAccuracyByRange]
    ) -> dict[tuple[float, float], SensorAccuracyByRange]:
        # Ensure range_min is less than range_max
        for rg in accs:
            if not rg[0] < rg[1]:
                raise ValueError(
                    f"Minimum range value {rg[0]} of accuracies must be strictly less than maximum range value {rg[1]}"
                )
        # Sort the original keys from min to max based on range_min
        return dict(sorted(accs.items(), key=lambda item: item[0][0]))

    @model_validator(mode='after')
    def validate_accuracies(self) -> 'SingleSensorBase':
        # Convert keys of accuracies to list
        accs = list(self.accuracies)

        # Check if accuracy profiles do not cover the entire measurement range
        if accs[0][0] != self.range[0]:
            raise ValueError(
                f"Inconsistent minimal measurement range between class SensorBase {self.range[0]} and class "
                f"SensorAccuracyByRange {accs[0][0]}"
            )
        if accs[-1][1] != self.range[1]:
            raise ValueError(
                f"Inconsistent maximal measurement range between class SensorBase {self.range[1]} and class "
                f"SensorAccuracyByRange {accs[-1][1]}"
            )

        # Check if accuracy profiles are continuously on the measurement range
        for i in range(len(accs)):
            if i > 0 and accs[i - 1][1] + self.resolution != accs[i][0]:
                raise ValueError(
                    f"Discontinuous definition of accuracy between ranges ({accs[i - 1][0]}, {accs[i - 1][1]}) and "
                    f"({accs[i][0]}, {accs[i][1]}), the difference between {accs[i - 1][1]} in ({accs[i - 1][0]}, "
                    f"{accs[i - 1][1]}) and {accs[i][0]} in ({accs[i][0]}, {accs[i][1]}) must be the resolution of "
                    f"{self.resolution}"
                )
        return self

    sensing_technology: str | None = Field(
        default=None,
        title='Sensing technology',
        description='Sensing technology of the sensor, e.g. NTC, NDIR, piezo',
        validation_alias=AliasChoices('sensing technology'),
    )

    note: str | None = Field(
        default=None,
        title='Note',
        description='Note for the sensor, e.g. additional conditions for accuracy, long-term stability',
    )

    calibration_date: date | None = Field(
        default=None,
        title='Calibration date',
        description='Calibration date of the sensor',
        validation_alias=AliasChoices('calibration date', 'date of calibration'),
        ge=date(1900, 1, 1),
        le=date.today()
    )

    def calculate_error(self, measured_value: float) -> float:
        """Calculate measurement error"""
        for acc, val in self.accuracies.items():
            if acc[0] <= measured_value <= acc[1]:
                return val.calculate_error(measured_value)

        raise ValueError(
            f"Measured value {measured_value} {self.unit} does not match any accuracy ranges for this sensor")


class MultiSensorBase(SensorABC):
    # Discriminator
    sensor_type: Literal['multi'] = 'multi'

    # Sensors
    sensors: dict[str, SingleSensorBase] = Field(
        default_factory=dict,
        title='Sensors',
        description='Sensors in multi-sensor product, in format {<sensor_id>: SensorBase}',
        min_length=1,
    )
