from datetime import date
import json
import pytest
from pydantic import ValidationError
from ieqstar.metadata.sensor import SensorBase, SensorAccuracyByRange


class TestInstantiation:
    """Verify instantiation of InstrumentBase"""
    def test_from_dict(self, valid_data_sensor_co2):
        """Instantiation of InstrumentBase from a dictionary"""
        sensor = SensorBase(**valid_data_sensor_co2)
        assert sensor.manufacturer == 'Test Mfr'
        assert sensor.model_name == 'Test Sen CO2'
        assert sensor.serial_number == 'S/N 1234 5678'
        assert sensor.measurand == 'CO2'
        assert sensor.unit == 'ppm'
        assert sensor.range == (0, 10000)
        assert sensor.resolution == 1.0
        assert sensor.calibration_date == date(2026, 1, 1)
        assert isinstance(sensor.accuracies[0], SensorAccuracyByRange)
        assert sensor.accuracies[0].range == (0, 5000)

    def test_from_json(self, valid_data_sensor_co2):
        """Instantiation of InstrumentBase from a JSON string"""
        sensor_from_dict = SensorBase(**valid_data_sensor_co2)
        json_string = json.dumps(valid_data_sensor_co2)
        sensor_from_json = SensorBase.model_validate_json(json_string)
        assert sensor_from_dict == sensor_from_json


class TestRangeValidation:
    """Verify range validation"""
    def test_range_validation(self, valid_data_sensor_co2):
        """Verify invalid sensor range"""
        valid_data_sensor_co2['range'] = (5000, 0)
        with pytest.raises(ValidationError) as e:
            SensorBase(**valid_data_sensor_co2)
        assert "Minimum range value 5000.0 must be strictly less than maximum range value 0.0" in str(e.value)

    def test_range_accuracy_inconsistent_min(self, valid_data_sensor_co2):
        """Verify inconsistency between sensor range and minimal accuracy range"""
        valid_data_sensor_co2['accuracies'][0]['range'] = (-500, 5000)
        with pytest.raises(ValidationError) as e:
            SensorBase(**valid_data_sensor_co2)
        assert "Inconsistent minimal measurement range" in str(e.value)

    def test_range_accuracy_inconsistent_max(self, valid_data_sensor_co2):
        """Verify inconsistency between sensor range and maximal accuracy range"""
        valid_data_sensor_co2['accuracies'][-1]['range'] = (5001, 8000)
        with pytest.raises(ValidationError) as e:
            SensorBase(**valid_data_sensor_co2)
        assert "Inconsistent maximal measurement range" in str(e.value)

    def test_range_accuracy_discontinuous(self, valid_data_sensor_co2):
        """Verify discontinoous accuracy ranges"""
        valid_data_sensor_co2['accuracies'][-1]['range'] = (5000, 10000)
        with pytest.raises(ValidationError) as e:
            SensorBase(**valid_data_sensor_co2)
        assert "Discontinuous definition of accuracy" in str(e.value)


class TestErrorCalculation:
    """Verify error calculation"""
    @pytest.mark.parametrize(
        "measured_value, expected_error",
        [(0, 50), (1000, 80), (5000, 200), (5001, 350.05), (8000, 500), (10000, 600)]
    )
    def test_calculate_error_add(self, valid_data_sensor_co2, measured_value, expected_error):
        """Verify error calculation with 'add' function"""
        sensor = SensorBase(**valid_data_sensor_co2)
        assert sensor.calculate_error(measured_value) == pytest.approx(expected_error)

    @pytest.mark.parametrize(
        "measured_value, expected_error",
        [(0, 50), (1000, 50), (5000, 150), (5001, 250.05), (8000, 400), (10000, 500)]
    )
    def test_calculate_error_max(self, valid_data_sensor_co2, measured_value, expected_error):
        """Verify error calculation with 'max' function"""
        for acc in valid_data_sensor_co2['accuracies']:
            acc['error_combination'] = 'max'
        sensor = SensorBase(**valid_data_sensor_co2)
        assert sensor.calculate_error(measured_value) == pytest.approx(expected_error)

    def test_calculate_error_out_of_bounds(self, valid_data_sensor_co2):
        """Verify error calculation with measured value out of bounds"""
        sensor = SensorBase(**valid_data_sensor_co2)
        with pytest.raises(ValueError) as e:
            sensor.calculate_error(measured_value=20000)
        assert "does not match any accuracy ranges" in str(e.value)

    def test_accuracies_sorting(self, valid_data_sensor_co2):
        """Verify accuracies sorted correctly"""
        valid_data_sensor_co2['accuracies'].reverse()  # Reverse accuracies sequence of input
        sensor = SensorBase(**valid_data_sensor_co2)
        assert sensor.accuracies[0].range == (0, 5000)
        assert sensor.accuracies[1].range == (5001, 10000)
