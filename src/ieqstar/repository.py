import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from pydantic import TypeAdapter

from .metadata.field import FieldBase
from .metadata.sensor import MultiSensorBase, SingleSensorBase
from .metadata.subject import SubjectBase

logger = logging.getLogger(__name__)


class RepositoryABC(ABC):
    """Manage the basic operations of an IEQ-STAR repository"""
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    @abstractmethod
    def initialize_repo(self) -> None:
        """Create the file structure for the repository"""
        pass


class RepositoryMetadata(RepositoryABC):
    """Manage the basic operations of an IEQ-STAR repository of metadata"""
    def __init__(self, root_dir: str | Path):
        super().__init__(root_dir)
        self.metadata_dir = self.root_dir / "metadata"
        self.field_dir = self.metadata_dir / "fields"
        self.sensor_dir = self.metadata_dir / "sensors"
        self.subject_dir = self.metadata_dir / "subjects"

    def initialize_repo(self) -> None:
        dirs = [self.field_dir, self.sensor_dir, self.subject_dir]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_field(file_path: str | Path) -> FieldBase:
        """Load a field from the file path"""
        json_str = Path(file_path).read_text(encoding="utf-8")
        return FieldBase.model_validate_json(json_str)

    def save_field(self, field: FieldBase, field_dir: str | Path | None = None) -> None:
        """Save a field to the repository"""
        json_str = field.model_dump_json(indent=2)
        file_name = f"{field.name}.json"
        file_path = self.field_dir / file_name if field_dir is None else field_dir / file_name
        file_path.write_text(data=json_str, encoding="utf-8")

    @staticmethod
    def load_sensor(file_path: str | Path) -> SingleSensorBase | MultiSensorBase:
        """Load a field from the file path"""
        json_str = Path(file_path).read_text(encoding="utf-8")
        sensor_adapter = TypeAdapter(Union[SingleSensorBase, MultiSensorBase])
        return sensor_adapter.validate_python(json_str)

    def save_sensor(self, sensor: SingleSensorBase | MultiSensorBase, sensor_dir: str | Path | None = None) -> None:
        """Save a sensor to the repository"""
        json_str = sensor.model_dump_json(indent=2)
        file_name = f"{sensor.sensor_type}_{sensor.manufacturer}_{sensor.model_name}_{sensor.serial_number}.json"
        file_path = self.sensor_dir / file_name if sensor_dir is None else sensor_dir / file_name
        file_path.write_text(data=json_str, encoding="utf-8")

    @staticmethod
    def load_subject(file_path: str | Path) -> SubjectBase:
        """Load a subject from the file path"""
        json_str = Path(file_path).read_text(encoding="utf-8")
        return SubjectBase.model_validate_json(json_str)

    def save_subject(self, subject: SubjectBase, subject_dir: str | Path | None = None) -> None:
        """Save a subject to the repository"""
        json_str = subject.model_dump_json(indent=2)
        file_name = f"{subject.id_short}_{subject.first_name}_{subject.last_name}.json"
        file_path = self.subject_dir / file_name if subject_dir is None else subject_dir / file_name
        file_path.write_text(data=json_str, encoding="utf-8")
