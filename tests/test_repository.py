import pytest

from ieqstar.metadata.field import FieldBase
from ieqstar.metadata.sensor import MultiSensorBase, SingleSensorBase
from ieqstar.metadata.subject import SubjectBase
from ieqstar.repository import RepositoryMetadata


@pytest.fixture
def repo_root_dir(tmp_path):
    """Temporary root directory for tests"""
    return tmp_path / "ieqstar_repo"

@pytest.fixture
def initialized_repo_metadata(repo_root_dir):
    """Initialized repo of class RepositoryMetadata"""
    repo = RepositoryMetadata(repo_root_dir)
    repo.initialize_repo()
    return repo

@pytest.fixture
def valid_field_base(valid_data_field):
    """Valid instance of class FieldBase"""
    return FieldBase(**valid_data_field)

@pytest.fixture
def valid_single_sensor_base(valid_data_sensor_co2):
    """Valid instance of class SingleSensorBase"""
    return SingleSensorBase(**valid_data_sensor_co2)

@pytest.fixture
def valid_multi_sensor_base(valid_data_multi_sensor):
    """Valid instance of class MultiSensorBase"""
    return MultiSensorBase(**valid_data_multi_sensor)

@pytest.fixture
def valid_subject_base(valid_data_subject):
    """Valid instance of class SubjectBase"""
    return SubjectBase(**valid_data_subject)


class TestRepositoryMetadata:
    def test_initialize_repo(self, repo_root_dir):
        repo = RepositoryMetadata(root_dir=repo_root_dir)
        assert not repo.root_dir.exists()  # Before initializing, check dir do not exist
        repo.initialize_repo()
        assert repo.metadata_dir.is_dir()  # After initializing, check dir
        assert repo.field_dir.is_dir()
        assert repo.sensor_dir.is_dir()
        assert repo.subject_dir.is_dir()

    def test_save_and_load_field(self, initialized_repo_metadata, valid_field_base):
        # Test save
        initialized_repo_metadata.save_field(field=valid_field_base)
        expected_file = initialized_repo_metadata.field_dir / "Test field.json"
        assert expected_file.exists()

        # Test load
        loaded_field = initialized_repo_metadata.load_field(file_path=expected_file)
        assert loaded_field == valid_field_base

    def test_save_and_load_sensor(
            self,
            initialized_repo_metadata,
            valid_single_sensor_base,
            valid_multi_sensor_base
    ):
        # Test save
        initialized_repo_metadata.save_sensor(sensor=valid_single_sensor_base)
        expected_file_single_sensor = initialized_repo_metadata.sensor_dir / "single_TestMfr_TestSenCO2_SN12345678.json"
        assert expected_file_single_sensor.exists()

        initialized_repo_metadata.save_sensor(sensor=valid_multi_sensor_base)
        expected_file_multi_sensor = initialized_repo_metadata.sensor_dir / "multi_TestMfrMS_TestMulti_SNMT123.json"
        assert expected_file_multi_sensor.exists()

        # Test load
        loaded_single_sensor = initialized_repo_metadata.load_sensor(file_path=expected_file_single_sensor)
        assert loaded_single_sensor == valid_single_sensor_base

        loaded_multi_sensor = initialized_repo_metadata.load_sensor(file_path=expected_file_multi_sensor)
        assert loaded_multi_sensor == valid_multi_sensor_base

    def test_save_and_load_subject(self, initialized_repo_metadata, valid_subject_base):
        # Test save
        initialized_repo_metadata.save_subject(subject=valid_subject_base)
        expected_file = initialized_repo_metadata.subject_dir / "28dcc51d_Max_Mustermann.json"
        assert expected_file.exists()

        # Test load
        loaded_subject = initialized_repo_metadata.load_subject(file_path=expected_file)
        assert loaded_subject == valid_subject_base
