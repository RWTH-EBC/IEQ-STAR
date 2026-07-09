import pytest

from ieqstar import __version__
from ieqstar.metadata.field import FieldBase


class TestInstantiation:
    """Verify instantiation of FieldBase"""
    def test_from_dict(self, valid_data_field):
        """Instantiation of FieldBase from a dictionary"""
        field = FieldBase(**valid_data_field)
        assert field.ieq_star_version == __version__
        assert field.name == "Test field"
        assert field.length == 2.0
        assert field.width == 2.0
        assert field.height == 2.5
        assert field.area == pytest.approx(4.0)  # Confirm computed field
        assert field.volume == pytest.approx(10.0)  # Confirm computed field

    def test_from_json(self, valid_data_field):
        """Instantiation of FieldBase from a JSON string"""
        field_from_dict = FieldBase(**valid_data_field)
        json_string = field_from_dict.model_dump_json(indent=2)
        field_from_json = FieldBase.model_validate_json(json_string)
        assert field_from_json == field_from_dict
