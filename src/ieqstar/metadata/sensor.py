from datetime import date
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


class SensorAccuracyErrorCombination(str, Enum):
    """Combinations of absolute and relative errors for sensor accuracy calculation"""
    ADD = 'add'  # Add values of absolute and relative errors
    MAX = 'max'  # Max value of absolute and relative errors


class SensorAccuracyByRange(BaseModel):
    """Sensor accuracy by a specific range"""
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    range: tuple[float, float] = Field(
        title='Range',
        description='Measurement range for the accuracy (required field), in (min, max)',
    )

    # Validate range
    @field_validator('range')
    @classmethod
    def validate_range(cls, rg: tuple[float, float]) -> tuple[float, float]:
        """Ensure minimum is less than maximum range"""
        if not rg[0] < rg[1]:
            raise ValueError(f"Minimum range value {rg[0]} must be strictly less than maximum range value {rg[1]}")
        return rg

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
        elif self.error_combination == SensorAccuracyErrorCombination.MAX:
            return max(self.absolute_error, self.relative_error * abs(measured_value))
        else:
            raise ValueError(f"Error combination {self.error_combination} not implemented")


class SensorBase(BaseModel):
    """Sensor or transducer"""
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    id: str = Field(
        title='ID',
        description='ID to distinguish sensors (required field)',
        validation_alias=AliasChoices('ID'),
    )

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
                    'entire batch or line of instruments',
        validation_alias=AliasChoices('model', 'type', 'type code', 'module', 'module type', 'part number', 'P/N',
                                      'PN'),
        min_length=1,
        max_length=50,
    )

    serial_number: str | None = Field(
        default=None,
        title='Serial number',
        description='Serial number, which is a completely unique identifier assigned to one specific instrument',
        validation_alias=AliasChoices('serial number', 'S/N', 'SN'),
        min_length=1,
        max_length=50,
    )

    measurand: str = Field(
        title='Measurand',
        description='Measurand (required field), defined as the physical quantity that the sensor intends to measure',
        # Ref: https://www.sciencedirect.com/topics/engineering/measurand
        validation_alias=AliasChoices('parameter', 'variable', 'value'),
        min_length=2,
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
            raise ValueError(f"Minimum range value {rg[0]} must be strictly less than maximum range value {rg[1]}")
        return rg

    resolution: float = Field(
        title='Resolution',
        description='Measurement resolution (required field)',
        gt=0,
    )

    accuracies: list[SensorAccuracyByRange] = Field(
        default_factory=list,
        title='Accuracies',
        description='Measurement accuracies by various ranges (required field)',
        min_length=1,
    )

    @model_validator(mode='after')
    def validate_accuracies(self) -> 'SensorBase':
        # Sort the original list in-place from min to max
        self.accuracies.sort(key=lambda acc: acc.range[0])

        # Check if accuracy profiles do not cover the entire measurement range
        if self.accuracies[0].range[0] != self.range[0]:
            raise ValueError(
                f"Inconsistent minimal measurement range between class Sensor {self.range[0]} and class "
                f"SensorAccuracyByRange {self.accuracies[0].range[0]}"
            )
        if self.accuracies[-1].range[1] != self.range[1]:
            raise ValueError(
                f"Inconsistent maximal measurement range between class Sensor {self.range[1]} and class "
                f"SensorAccuracyByRange {self.accuracies[-1].range[1]}"
            )

        # Check if accuracy profiles are continuously on the measurement range
        for i, acc in enumerate(self.accuracies):
            if i > 0 and self.accuracies[i - 1].range[1] + self.resolution != self.accuracies[i].range[0]:
                raise ValueError(
                    f"Discontinuous definition of accuracy between ranges ({self.accuracies[i - 1].range[0]}, "
                    f"{self.accuracies[i - 1].range[1]}) and ({self.accuracies[i].range[0]}, "
                    f"{self.accuracies[i].range[1]}), the difference between {self.accuracies[i - 1].range[1]} in "
                    f"({self.accuracies[i - 1].range[0]}, {self.accuracies[i - 1].range[1]}) and "
                    f"{self.accuracies[i].range[0]} in ({self.accuracies[i].range[0]}, "
                    f"{self.accuracies[i].range[1]}) must be the resolution of {self.resolution}"
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
    )

    def calculate_error(self, measured_value: float) -> float:
        """Calculate measurement error"""
        for acc in self.accuracies:
            if acc.range[0] <= measured_value <= acc.range[1]:
                return acc.calculate_error(measured_value)

        raise ValueError(
            f"Measured value {measured_value} {self.unit} does not match any accuracy ranges for this sensor")
