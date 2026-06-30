from pydantic import AliasChoices, BaseModel, ConfigDict, Field, computed_field


class FieldBase(BaseModel):
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    length: float = Field(
        title='Length',
        description='Field length (required field)',
        validation_alias=AliasChoices('L'),
        gt=0,
    )

    width: float = Field(
        title='Width',
        description='Field width (required field)',
        validation_alias=AliasChoices('W'),
        gt=0,
    )

    height: float = Field(
        title='Height',
        description='Field height (required field)',
        validation_alias=AliasChoices('H'),
        gt=0,
    )

    @computed_field
    @property
    def area(self) -> float:
        """Field area"""
        return self.length * self.width

    @computed_field
    @property
    def volume(self) -> float:
        """Field volume"""
        return self.area * self.height
