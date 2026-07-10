from datetime import date

import pytest
from pydantic import ValidationError

from ieqstar import __version__
from ieqstar.metadata.sensor import MultiSensorBase, SensorAccuracyByRange, SingleSensorBase


class TestSingleSensorInstantiation:
    """Verify instantiation of SingleSensorBase"""
    def test_from_dict(self, valid_data_sensor_co2):
        """Instantiation of SingleSensorBase from a dictionary"""
        sensor = SingleSensorBase(**valid_data_sensor_co2)
        assert sensor.ieq_star_version == __version__
        assert sensor.manufacturer == "Test Mfr"
        assert sensor.model_name == "Test Sen CO2"
        assert sensor.serial_number == "S/N 1234 5678"
        assert sensor.measurand == "CO2 concentration"
        assert sensor.unit == "ppm"
        assert sensor.range == (0, 10000)
        assert sensor.resolution == 1.0
        assert list(sensor.accuracies)[0] == (0, 5000)
        assert isinstance(list(sensor.accuracies.values())[0], SensorAccuracyByRange)
        assert sensor.calibration_date == date(2026, 1, 1)

    def test_from_json(self, valid_data_sensor_co2):
        """Instantiation of SingleSensorBase from a JSON string"""
        sensor_from_dict = SingleSensorBase(**valid_data_sensor_co2)
        json_string = sensor_from_dict.model_dump_json(indent=2)
        sensor_from_json = SingleSensorBase.model_validate_json(json_string)
        assert sensor_from_json == sensor_from_dict


class TestSingleSensorRangeValidation:
    """Verify range validation"""
    def test_range_validation(self, valid_data_sensor_co2):
        """Verify invalid sensor range"""
        valid_data_sensor_co2['range'] = (10000, 0)
        with pytest.raises(ValidationError) as e:
            SingleSensorBase(**valid_data_sensor_co2)
        assert "Minimum range value" in str(e.value) and "of sensor" in str(e.value)

    def test_range_accuracy_inconsistent_min(self, valid_data_sensor_co2):
        """Verify inconsistency between sensor range and minimal accuracy range"""
        valid_data_sensor_co2['accuracies'][(-500, 5000)] = valid_data_sensor_co2['accuracies'].pop((0, 5000))
        with pytest.raises(ValidationError) as e:
            SingleSensorBase(**valid_data_sensor_co2)
        assert "Inconsistent minimal measurement range" in str(e.value)

    def test_range_accuracy_inconsistent_max(self, valid_data_sensor_co2):
        """Verify inconsistency between sensor range and maximal accuracy range"""
        valid_data_sensor_co2['accuracies'][(5001, 8000)] = valid_data_sensor_co2['accuracies'].pop((5001, 10000))
        with pytest.raises(ValidationError) as e:
            SingleSensorBase(**valid_data_sensor_co2)
        assert "Inconsistent maximal measurement range" in str(e.value)

    def test_range_accuracy_discontinuous(self, valid_data_sensor_co2):
        """Verify discontinuous accuracy ranges"""
        valid_data_sensor_co2['accuracies'][(5000, 10000)] = valid_data_sensor_co2['accuracies'].pop((5001, 10000))
        with pytest.raises(ValidationError) as e:
            SingleSensorBase(**valid_data_sensor_co2)
        assert "Discontinuous definition of accuracy" in str(e.value)


class TestSingleSensorErrorCalculation:
    """Verify error calculation"""
    @pytest.mark.parametrize(
        "measured_value, expected_error",
        [(0, 50), (1000, 80), (5000, 200), (5001, 350.05), (8000, 500), (10000, 600)]
    )
    def test_calculate_error_add(self, valid_data_sensor_co2, measured_value, expected_error):
        """Verify error calculation with 'add' function"""
        sensor = SingleSensorBase(**valid_data_sensor_co2)
        assert sensor.calculate_error(measured_value) == pytest.approx(expected_error)

    @pytest.mark.parametrize(
        "measured_value, expected_error",
        [(0, 50), (1000, 50), (5000, 150), (5001, 250.05), (8000, 400), (10000, 500)]
    )
    def test_calculate_error_max(self, valid_data_sensor_co2, measured_value, expected_error):
        """Verify error calculation with 'max' function"""
        for v in valid_data_sensor_co2['accuracies'].values():
            v['error_combination'] = 'max'
        sensor = SingleSensorBase(**valid_data_sensor_co2)
        assert sensor.calculate_error(measured_value) == pytest.approx(expected_error)

    def test_calculate_error_out_of_bounds(self, valid_data_sensor_co2):
        """Verify error calculation with measured value out of bounds"""
        sensor = SingleSensorBase(**valid_data_sensor_co2)
        with pytest.raises(ValueError) as e:
            sensor.calculate_error(measured_value=20000)
        assert "does not match any accuracy ranges" in str(e.value)

    def test_accuracies_sorting(self, valid_data_sensor_co2):
        """Verify accuracies sorted correctly"""
        reversed_accuracies = dict(reversed(valid_data_sensor_co2['accuracies'].items()))
        valid_data_sensor_co2['accuracies'] = reversed_accuracies  # Reverse accuracies sequence of input
        sensor = SingleSensorBase(**valid_data_sensor_co2)
        assert list(sensor.accuracies)[0] == (0, 5000)
        assert list(sensor.accuracies)[1] == (5001, 10000)


class TestMultiSensorInstantiation:
    """Verify instantiation of MultiSensorBase"""
    def test_from_dict(self, valid_data_multi_sensor):
        """Instantiation of MultiSensorBase from dictionary"""
        multi_sensor = MultiSensorBase(**valid_data_multi_sensor)
        assert multi_sensor.ieq_star_version == __version__
        assert multi_sensor.manufacturer == "Test Mfr MS"
        assert len(multi_sensor.sensors) == 2
        assert multi_sensor.sensors['Temp_1'].manufacturer == "Test Mfr"
        assert multi_sensor.sensors['Temp_2'].manufacturer == "Test Mfr MS"

    def test_from_json(self, valid_data_multi_sensor):
        """Instantiation of MultiSensorBase from a JSON string"""
        multi_sensor_from_dict = MultiSensorBase(**valid_data_multi_sensor)
        json_string = multi_sensor_from_dict.model_dump_json(indent=2)
        multi_sensor_from_json = MultiSensorBase.model_validate_json(json_string)
        assert multi_sensor_from_json == multi_sensor_from_dict
