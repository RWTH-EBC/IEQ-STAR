from abc import ABC

from pydantic import BaseModel, ConfigDict, Field

from ieqstar import __version__

GLOBAL_MODEL_CONFIG = ConfigDict(
    validate_assignment=True,
    validate_by_name=True,
)

class MetadataABC(BaseModel, ABC):
    model_config = GLOBAL_MODEL_CONFIG

    ieq_star_version: str = Field(
        default=__version__,
        title="IEQ-STAR version",
        description="Current version of IEQ-STAR",
    )
