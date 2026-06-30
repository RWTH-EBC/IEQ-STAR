import hashlib
from abc import ABC
from datetime import date
from enum import Enum

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_extra_types.phone_numbers import PhoneNumber


class Sex(str, Enum):
    """
    Genotypic (chromosomal) sex
    Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/person_genotypic_sex__national_neonatal_data_set_.html
    """
    MALE = 'male'
    FEMALE = 'female'
    INTERSEX = 'indeterminate/intersex'


class Gender(str, Enum):
    """
    Gender identity or role
    Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/gender_identity_code.html
    """
    MALE = 'male'  # Including trans man
    FEMALE = 'female'  # Including trans women
    NON_BINARY = 'non-binary'
    OTHER = 'other'  # Not listed
    NOT_STATED = 'not-stated'  # Asked but declined to provide a response


class MeasurementLog(BaseModel, ABC):
    """Single log of a measurement, e.g. height and weight"""
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    log_date: date = Field(
        title='Log date',
        description='Log date (required field)',
        validation_alias=AliasChoices('log date', 'date'),
        ge=date(1900, 1, 1),
        le=date.today(),
    )


class HeightLog(MeasurementLog):
    """Single log of a measurement of height"""
    height: float = Field(
        title='Height',
        description='Height in m (required field)',
        ge=0.50,
        le=2.50,
    )

    # Round the height value
    @field_validator('height')
    @classmethod
    def round_height(cls, v: float) -> float:
        # Round value to two decimals
        return round(v, 2)


class WeightLog(MeasurementLog):
    """Single log of a measurement of weight"""
    weight: float = Field(
        title='Weight',
        description='Weight in kg (required field)',
        ge=5.0,
        le=250.0,
    )

    # Round the weight value
    @field_validator('weight')
    @classmethod
    def round_weight(cls, v: float) -> float:
        # Round value to one decimal
        return round(v, 1)


class SubjectBase(BaseModel):
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_by_name=True,
    )

    # Names
    last_name_at_birth: str = Field(
        frozen=True,
        title='Last name at birth',
        description='Last name at birth (required field)',
        validation_alias=AliasChoices('last name at birth', 'birth name', 'birth surname', 'maiden name'),
        min_length=1,
        max_length=35,  # Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/person_family_name__at_birth_.html
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$"
    )

    last_name: str | None = Field(
        default=None,
        title='Last name',
        description='Last name, default same as last name at birth',
        validation_alias=AliasChoices('last name', 'family name', 'surname'),
        min_length=1,
        max_length=35,  # Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/patient_family_name.html
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$"
    )

    # Set default last name
    @model_validator(mode='after')
    def set_default_last_name(self) -> 'SubjectBase':
        """Set default last name same as last name at birth"""
        if self.last_name is None:
            self.last_name = self.last_name_at_birth
        return self

    first_name: str = Field(
        frozen=True,
        title='First name',
        description='First name (required field)',
        validation_alias=AliasChoices('first name', 'given name', 'forename'),
        min_length=1,
        max_length=35,  # Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/patient_given_name.html
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$"
    )

    middle_name: str | None = Field(
        default=None,
        title='Middle name',
        description='Middle name',
        validation_alias=AliasChoices('middle name', 'second name', 'second given name'),
        min_length=1,
        max_length=255,
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$"
    )

    # Birth
    birth_date: date = Field(
        frozen=True,
        title='Date of birth',
        description='Date of birth (required field)',
        validation_alias=AliasChoices('birth date', 'birthday', 'date of birth'),
        ge=date(1900, 1, 1),
        le=date.today(),
    )

    # Sex and gender
    # Sex-gender distinction: https://medicine.yale.edu/news-article/what-do-we-mean-by-sex-and-gender/
    sex: Sex | None = Field(
        default=None,
        title='Sex',
        description='Genotypic (chromosomal) sex, generally as male or female, according to the chromosomal complement',
        validation_alias=AliasChoices('sex at birth', 'birth sex', 'natal sex', 'biological sex')
    )

    gender: Gender = Field(
        title='Gender',
        description='Gender identity (required field), which refers to self-representation influenced by social, '
                    'cultural, and personal experience',
        validation_alias=AliasChoices('gender identity'),
    )

    # Measurement logs
    height_logs: list[HeightLog] = Field(
        default_factory=list,
        title='Height logs',
        description='Historical logs of height',
        validation_alias=AliasChoices('height logs', 'heights')
    )

    weight_logs: list[WeightLog] = Field(
        default_factory=list,
        title='Weight logs',
        description='Historical logs of weight',
        validation_alias=AliasChoices('weight logs', 'weights')
    )

    # Validate unique log dates for all logs
    @field_validator('height_logs', 'weight_logs')
    @classmethod
    def validate_unique_dates_of_logs(cls, logs: list[MeasurementLog]) -> list[MeasurementLog]:
        # Sort the original list in-place from min to max based on log_date
        logs.sort(key=lambda log: log.log_date)

        # Ensure all log dates in a historical logs are unique
        dates_found = set()
        for log in logs:
            if log.log_date in dates_found:
                raise ValueError(
                    f"Duplicated log entry: historical log found for date {log.log_date.strftime('%Y-%m-%d')}"
                )
            else:
                dates_found.add(log.log_date)
        return logs

    # Contact
    phone: PhoneNumber | None = Field(
        default=None,
        title='Phone',
        description='Phone number',
        validation_alias=AliasChoices('phone number'),
    )

    email: EmailStr | None = Field(
        default=None,
        title='Email',
        description='Email address',
        validation_alias=AliasChoices('Email', 'E-Mail', 'E-mail'),
    )

    # Documents of metadata
    registration_date: date = Field(
        default=date.today(),
        title='Date of registration',
        description='Date of registration (automatically assigned when generating the instance)',
        validation_alias=AliasChoices('registration date', 'date of registration'),
        ge=date(1900, 1, 1),
        le=date.today(),
    )

    # Identifiers
    @computed_field
    @property
    def pii(self) -> str:
        """Personally identifiable information (PII)"""
        def keep_only_characters(s: str) -> str:
            """Only keep characters of a string, including non-latin characters"""
            return "".join(char for char in s if char.isalpha())

        def get_gender_abbr(gender: Gender) -> str:
            """Convert gender enumeration to abbreviation"""
            mapping = {
                Gender.MALE: 'm',
                Gender.FEMALE: 'f',
                Gender.NON_BINARY: 'nb',
                Gender.OTHER: 'o',
                Gender.NOT_STATED: 'ns',
            }
            return mapping[gender]

        first_name_pii = keep_only_characters(self.first_name).lower()
        last_name_at_birth_pii = keep_only_characters(self.last_name_at_birth).lower()
        birth_data_pii = self.birth_date.strftime('%Y-%m-%d')
        gender_pii = get_gender_abbr(self.gender)

        return f"{first_name_pii}|{last_name_at_birth_pii}|{birth_data_pii}|{gender_pii}"

    @computed_field
    @property
    def id_full(self) -> str:
        """Full ID, generated by SHA-256 from PII"""
        return hashlib.sha256(self.pii.encode()).hexdigest().lower()

    @computed_field
    @property
    def id_short(self) -> str:
        """Short ID, first eight digits of full ID"""
        return self.id_full[:8]
