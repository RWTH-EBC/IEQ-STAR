import pytest


@pytest.fixture
def valid_data_subject() -> dict:
    """Valid data of a subject"""
    return {
        'last_name_at_birth': 'Mustermann',
        'first_name': 'Max',
        'middle_name': 'Maria',
        'birth_date': '1992-05-20',
        'gender': 'male',
        'height_logs': [
            {'log_date': '2026-01-01', 'height': 1.789},
            {'log_date': '2026-03-01', 'height': 1.78},
            {'log_date': '2026-02-01', 'height': 1.79},
        ],
        'weight_logs': [
            {'log_date': '2026-01-01', 'weight': 67.89},
            {'log_date': '2026-03-01', 'weight': 68.0},
            {'log_date': '2026-02-01', 'weight': 67.8},
        ],
        'phone': '+4917612345678',
        'email': 'max.mustermann@sub-domain.domain.de',
    }

@pytest.fixture
def valid_data_sensor_co2() -> dict:
    """Valid data of a CO2 sensor as example"""
    return {
        'manufacturer': 'Test Mfr',
        'model_name': 'Test Sen CO2',
        'serial_number': 'S/N 1234 5678',
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
        'note': 'Operating tempearture -5 °C to +50 °C',
        'calibration_date': '2026-01-01',
    }
