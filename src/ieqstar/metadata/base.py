from abc import ABC

from pydantic import BaseModel, ConfigDict, Field

from ieqstar import __version__


class MetadataBase(BaseModel, ABC):
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    version: str = Field(
        default=__version__,
        title="Version",
        description="Current version of IEQ-STAR",
    )
