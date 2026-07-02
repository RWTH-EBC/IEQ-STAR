import hashlib
from datetime import date
from enum import Enum

from pydantic import (
    AliasChoices,
    EmailStr,
    Field,
    TypeAdapter,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_extra_types.phone_numbers import PhoneNumber

from . import base


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


class SubjectBase(base.MetadataBase):
    # Names
    last_name_at_birth: str = Field(
        frozen=True,
        title='Last name at birth',
        description='Last name at birth (required field)',
        validation_alias=AliasChoices('last name at birth', 'birth name', 'birth surname', 'maiden name'),
        min_length=1,
        max_length=35,  # Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/person_family_name__at_birth_.html
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$",
    )

    last_name: str | None = Field(
        default=None,
        title='Last name',
        description='Last name, default same as last name at birth',
        validation_alias=AliasChoices('last name', 'family name', 'surname'),
        min_length=1,
        max_length=35,  # Ref: https://archive.datadictionary.nhs.uk/DD%20Release%20November%202025/data_elements/patient_family_name.html
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$",
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
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$",
    )

    middle_name: str | None = Field(
        default=None,
        title='Middle name',
        description='Middle name',
        validation_alias=AliasChoices('middle name', 'second name', 'second given name'),
        min_length=1,
        max_length=255,
        pattern=r"^[^\W\d_]+([ '-][^\W\d_]+)*$",
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
        validation_alias=AliasChoices('sex at birth', 'birth sex', 'natal sex', 'biological sex'),
    )

    gender: Gender = Field(
        title='Gender',
        description='Gender identity (required field), which refers to self-representation influenced by social, '
                    'cultural, and personal experience',
        validation_alias=AliasChoices('gender identity'),
    )

    # Measurement logs
    height_logs: dict[date, float] = Field(
        default_factory=dict,
        title='Height logs',
        description='Historical logs of height, in format {<log_date>: <height in m>}',
        validation_alias=AliasChoices('height logs', 'heights'),
    )

    @field_validator('height_logs')
    @classmethod
    def validate_height_logs(cls, logs: dict[date, float]) -> dict[date, float]:
        lb_date = date(1900, 1, 1)
        ub_date = date.today()
        lb_height = 0.50  # in m
        ub_height = 2.50  # in m
        logs_output = {}
        for log_date, height in logs.items():
            # Check bounds
            if not (lb_date <= log_date <= ub_date):
                raise ValueError(f"Log date of {log_date} is out of range of {lb_date} and {ub_date}")
            if not (lb_height <= height <= ub_height):
                raise ValueError(
                    f"Height of {height} m at {log_date} is out of range of {lb_height} m and {ub_height} m"
                )
            # Round value to two decimals
            logs_output[log_date] = round(height, 2)
        # Sort by date
        logs_output = dict(sorted(logs_output.items()))
        return logs_output

    weight_logs: dict[date, float] = Field(
        default_factory=dict,
        title='Weight logs',
        description='Historical logs of weight, in format {<log_date>: <weight in kg>}',
        validation_alias=AliasChoices('weight logs', 'weights'),
    )

    @field_validator('weight_logs')
    @classmethod
    def validate_weight_logs(cls, logs: dict[date, float]) -> dict[date, float]:
        lb_date = date(1900, 1, 1)
        ub_date = date.today()
        lb_weight = 5.0  # in kg
        ub_weight = 250.0 # in kg
        logs_output = {}
        for log_date, weight in logs.items():
            # Check bounds
            if not (lb_date <= log_date <= ub_date):
                raise ValueError(f"Log date of {log_date} is out of range of {lb_date} and {ub_date}")
            if not (lb_weight <= weight <= ub_weight):
                raise ValueError(
                    f"Weight of {weight} kg at {log_date} is out of range of {lb_weight} kg and {ub_weight} kg"
                )
            # Round value to one decimal
            logs_output[log_date] = round(weight, 1)
        # Sort by date
        logs_output = dict(sorted(logs_output.items()))
        return logs_output

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

    @staticmethod
    def _get_latest_measurement_log(logs: dict[date, float], target_date: date | str) -> dict[date, float]:
        """Get the latest measurement log to the target date from a log dict"""
        # Parse target_date to type 'date'
        target_date = TypeAdapter(date).validate_python(target_date)

        # Iterate backwards through the logs to find the match with log_date <= target_date
        for log_date, v in reversed(logs.items()):
            if log_date <= target_date:
                return {log_date: v}
        return {}

    def get_latest_height_log(self, target_date: date | str | None = None) -> dict[date, float]:
        """
        Get the latest height log to the target date
        :param target_date: The latest height log earlier than or equal to it, default is today
        :return: Dict of {<log_date>: <height>}, if no matched, returns empty dict
        """
        if target_date is None:
            target_date = date.today()
        return self._get_latest_measurement_log(logs=self.height_logs, target_date=target_date)

    def get_latest_weight_log(self, target_date: date | str | None = None) -> dict[date, float]:
        """
        Get the latest weight log to the target date
        :param target_date: The latest weight log earlier than or equal to it, default is today
        :return: Dict of {<log_date>: <weight>}, if no matched, returns empty dict
        """
        if target_date is None:
            target_date = date.today()
        return self._get_latest_measurement_log(logs=self.weight_logs, target_date=target_date)
