from datetime import date
import json
import pytest
from pydantic import ValidationError
from src.ieqstar.metadata.instrument import InstrumentBase, Sensor, SensorAccuracyByRange


@pytest.fixture
def valid_co2_sensor_data() -> dict:
    """Valid data of a CO2 sensor"""
    return {
        'manufacturer': 'Test Mfr',
        'model_name': 'Test Sen CO2',
        'serial_number': 'S/N 1234',
        'id': '234',
        'measurand': 'CO2',
        'unit': 'ppm',
        'range': (0, 10_000),
        'resolution': 1,
        'accuracies': [
            {
                'range': (0, 5_000),
                'absolute_error': 50,
                'relative_error': 0.03,
                'error_combination': 'add',
            },
            {
                'range': (5_001, 10_000),
                'absolute_error': 100,
                'relative_error': 0.05,
                'error_combination': 'add',
            },
        ],
        'sensing_technology': 'NDIR',
        'calibration_date': '2026-01-01',
    }


@pytest.fixture
def valid_temperature_sensor_data() -> dict:
    """Valid data of a temperature sensor"""
    return {
        'manufacturer': 'Test Mfr',
        'model_name': 'Test Sen T',
        'serial_number': 'S/N 5678',
        'id': '678',
        'measurand': 'temperature',
        'unit': 'degC',
        'range': (-100, 300),
        'resolution': 0.1,
        'accuracies': [
            {
                'range': (-100, 300),
                'absolute_error': 0.15,
                'relative_error': 0.002,
                'error_combination': 'add',
            },
        ],
        'sensing_technology': 'Pt100',
        'note': 'Accuracy Class A according to EN 60751',
        'calibration_date': '2026-02-01',
    }


@pytest.fixture
def valid_instrument_data(valid_co2_sensor_data, valid_temperature_sensor_data) -> dict:
    """Valid data of a instrument"""
    return {
        'manufacturer': 'Test Mfr',
        'model_name': 'Test Instrument',
        'serial_number': 'S/N 1234 5678',
        'sensors': [
            valid_co2_sensor_data,
            valid_temperature_sensor_data,
        ],
    }


class TestInstantiation:
    """Verify instantiation of InstrumentBase"""
    def test_from_dict(self, valid_instrument_data):
        """Instantiation of InstrumentBase from a dictionary"""
        instrument = InstrumentBase(**valid_instrument_data)
        assert instrument.manufacturer == 'Test Mfr'
        assert instrument.model_name == 'Test Instrument'
        assert instrument.serial_number == 'S/N 1234 5678'
        assert isinstance(instrument.sensors[0], Sensor)  # Confirm type of sensor instance
        assert instrument.sensors[0].manufacturer == 'Test Mfr'
        assert instrument.sensors[0].model_name == 'Test Sen CO2'
        assert instrument.sensors[0].serial_number == 'S/N 1234'
        assert instrument.sensors[0].measurand == 'CO2'
        assert instrument.sensors[0].unit == 'ppm'
        assert instrument.sensors[0].range == (0, 10000)
        assert instrument.sensors[0].resolution == 1.0
        assert instrument.sensors[0].calibration_date == date(2026, 1, 1)
        assert isinstance(instrument.sensors[0].accuracies[0], SensorAccuracyByRange)
        assert instrument.sensors[0].accuracies[0].range == (0, 5000)

    def test_from_json(self, valid_instrument_data):
        """Instantiation of InstrumentBase from a JSON string"""
        instrument_from_dict = InstrumentBase(**valid_instrument_data)
        json_string = json.dumps(valid_instrument_data)
        instrument_from_json = InstrumentBase.model_validate_json(json_string)
        assert instrument_from_dict == instrument_from_json


class TestSensorSetup:
    """Verify setup of sensor"""
    def test_range_validation(self, valid_co2_sensor_data):
        """Verify invalid sensor range"""
        valid_co2_sensor_data['range'] = (5000, 0)
        with pytest.raises(ValidationError) as e:
            Sensor(**valid_co2_sensor_data)
        assert "Minimum range value 5000.0 must be strictly less than maximum range value 0.0" in str(e.value)

    def test_range_accuracy_inconsistent_min(self, valid_co2_sensor_data):
        """Verify inconsistency between sensor range and minimal accuracy range"""
        valid_co2_sensor_data['accuracies'][0]['range'] = (-500, 5_000)
        with pytest.raises(ValidationError) as e:
            Sensor(**valid_co2_sensor_data)
        assert "Inconsistent minimal measurement range" in str(e.value)

    def test_range_accuracy_inconsistent_max(self, valid_co2_sensor_data):
        """Verify inconsistency between sensor range and maximal accuracy range"""
        valid_co2_sensor_data['accuracies'][-1]['range'] = (5_001, 8_000)
        with pytest.raises(ValidationError) as e:
            Sensor(**valid_co2_sensor_data)
        assert "Inconsistent maximal measurement range" in str(e.value)

    def test_range_accuracy_discontinuous(self, valid_co2_sensor_data):
        """Verify discontinoous accuracy ranges"""
        valid_co2_sensor_data['accuracies'][-1]['range'] = (5_000, 10_000)
        with pytest.raises(ValidationError) as e:
            Sensor(**valid_co2_sensor_data)
        assert "Discontinuous definition of accuracy" in str(e.value)

    @pytest.mark.parametrize(
        "measured_value, expected_error",
        [(0, 50), (1_000, 80), (5_000, 200), (5_001, 350.05), (8_000, 500), (10_000, 600)]
    )
    def test_calculate_error_add(self, valid_co2_sensor_data, measured_value, expected_error):
        """Verify error calculation with 'add' function"""
        sensor_co2 = Sensor(**valid_co2_sensor_data)
        assert sensor_co2.calculate_error(measured_value) == pytest.approx(expected_error)

    @pytest.mark.parametrize(
        "measured_value, expected_error",
        [(0, 50), (1_000, 50), (5_000, 150), (5_001, 250.05), (8_000, 400), (10_000, 500)]
    )
    def test_calculate_error_max(self, valid_co2_sensor_data, measured_value, expected_error):
        """Verify error calculation with 'max' function"""
        for acc in valid_co2_sensor_data['accuracies']:
            acc['error_combination'] = 'max'
        sensor_co2 = Sensor(**valid_co2_sensor_data)
        assert sensor_co2.calculate_error(measured_value) == pytest.approx(expected_error)

    def test_calculate_error_out_of_bounds(self, valid_co2_sensor_data):
        """Verify error calculation with measured value out of bounds"""
        sensor_co2 = Sensor(**valid_co2_sensor_data)
        with pytest.raises(ValueError) as e:
            sensor_co2.calculate_error(measured_value=20_000)
        assert "does not match any accuracy ranges" in str(e.value)

    def test_accuracies_sorting(self, valid_co2_sensor_data):
        """Verify accuracies sorted correctly"""
        valid_co2_sensor_data['accuracies'].reverse()
        sensor_co2 = Sensor(**valid_co2_sensor_data)
        assert sensor_co2.accuracies[0].range == (0, 5_000)
        assert sensor_co2.accuracies[1].range == (5_001, 10_000)
