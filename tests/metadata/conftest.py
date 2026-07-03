import pytest


@pytest.fixture
def valid_data_subject() -> dict:
    """Valid data of a subject"""
    return {
        'last_name_at_birth': 'Mustermann',
        'first_name': 'Max',
        'middle_name': 'Maria',
        'birth_date': '1992-05-20',
        'sex': 'male',
        'gender': 'male',
        'height_logs': {
            '2026-01-01': 1.789,
            '2026-03-01': 1.78,
            '2026-02-01': 1.79,
        },
        'weight_logs': {
            '2026-01-01': 67.89,
            '2026-03-01': 68.0,
            '2026-02-01': 67.8,
        },
        'phone': '+4917612345678',
        'email': 'max.mustermann@sub-domain.domain.de',
    }

@pytest.fixture
def valid_data_sensor_co2() -> dict:
    """Valid data of a CO2 sensor"""
    return {
        'manufacturer': 'Test Mfr',
        'model_name': 'Test Sen CO2',
        'serial_number': 'S/N 1234 5678',
        'measurand': 'CO2 concentration',
        'unit': 'ppm',
        'range': (0, 10_000),
        'resolution': 1,
        'accuracies': {
            (0, 5_000): {
                'absolute_error': 50,
                'relative_error': 0.03,
                'error_combination': 'add',
            },
            (5_001, 10_000): {
                'absolute_error': 100,
                'relative_error': 0.05,
                'error_combination': 'add',
            },
        },
        'sensing_technology': 'NDIR',
        'note': 'Operating tempearture -5 °C to +50 °C',
        'calibration_date': '2026-01-01',
    }

@pytest.fixture
def valid_data_sensor_temperature() -> dict:
    """Valid data of a temperature sensor"""
    return {
        'manufacturer': 'Test Mfr',
        'model_name': 'Test Sen T',
        'serial_number': 'S/N T123 456',
        'measurand': 'Temperature',
        'unit': 'degC',
        'range': (-50, 400),
        'resolution': 0.1,
        'accuracies': {
            (-50, 400): {
                'absolute_error': 0.3,
                'relative_error': 0.005,
                'error_combination': 'add',
            },
        },
        'sensing_technology': 'Pt100',
        'note': 'Class B according to IEC 60751',
        'calibration_date': '2026-02-01',
    }

@pytest.fixture
def valid_data_multi_sensor(valid_data_sensor_temperature) -> dict:
    """Valid data of a multi-sensor"""
    return {
        'manufacturer': 'Test Mfr MS',
        'model_name': 'Test Multi',
        'serial_number': 'S/N MT 123',
        'sensors': {
            'Temp_1': {
                **valid_data_sensor_temperature,
            },
            'Temp_2': {
                'manufacturer': 'Test Mfr MS',
                'measurand': 'Temperature',
                'unit': 'degC',
                'range': (-60, 200),
                'resolution': 0.1,
                'accuracies': {
                    (-60, 200): {
                        'absolute_error': 0.15,
                        'relative_error': 0.002,
                        'error_combination': 'add',
                    },
                },
                'sensing_technology': 'Pt1000',
                'note': 'Class A according to IEC 60751',
                'calibration_date': '2026-03-01',
            },
        },
    }

@pytest.fixture
def valid_data_field() -> dict:
    """Valid data of a field"""
    return {
        'length': 2.0,
        'width': 2.0,
        'height': 2.5,
    }
