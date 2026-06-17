from pydantic import BaseModel, ConfigDict, Field, AliasChoices, computed_field


class Room(BaseModel):
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    name: str = Field(
        title='Name',
        description='Room name (required field)',
        min_length=1,
        max_length=50,
    )

    length: float = Field(
        title='Length',
        description='Room length (required field)',
        validation_alias=AliasChoices('L'),
        gt=0,
    )

    width: float = Field(
        title='Width',
        description='Room width (required field)',
        validation_alias=AliasChoices('W'),
        gt=0,
    )

    height: float = Field(
        title='Height',
        description='Room height (required field)',
        validation_alias=AliasChoices('H'),
        gt=0,
    )

    @computed_field
    @property
    def area(self) -> float:
        """Room area"""
        return self.length * self.width

    @computed_field
    @property
    def volume(self) -> float:
        """Room volume"""
        return self.area * self.height


class FieldBase(BaseModel):
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    name: str = Field(
        title='Name',
        description='Field name (required field)',
        min_length=1,
        max_length=50,
    )

    rooms: list[Room] = Field(
        default_factory=list,
        title='Rooms',
        description='Rooms in the field'
    )
