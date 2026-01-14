import logging
import os
import random
import re
import string
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple
from uuid import uuid4

from django.core.validators import RegexValidator


logger = logging.getLogger(__name__)
ENVIRONMENT = os.environ.get("ENVIRONMENT", None)
APP_ENV = "🚀 Production" if ENVIRONMENT == "production" else "🚧 Staging"


ADMIN_SIDEBAR_MODULES = [
    "OVERVIEW",
    "USER",
    "USER_KYC",
    "TRANSACTION",
    "DISPUTE",
    "MERCHANT",
    "THIRD_PARTY",
    "SETTINGS",
    "EVENT",
    "REFERRER",
    "CMS",
    "EMAIL_PROVIDER",
    "PAYMENT_GATEWAY",
]

def parse_datetime(datetime_input):
    try:
        val = str(datetime_input)[:-6]  # Remove timezone offset
        parsed_datetime = datetime.fromisoformat(val)
        parsed_datetime += timedelta(hours=1)  # Apply 1-hour offset
        return parsed_datetime.strftime("%B %d, %Y %I:%M%p")
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse datetime input '{datetime_input}': {e}")
        return ""


def parse_datetime_to_date(datetime_input):
    dt = (
        parse_datetime(datetime_input)
        if isinstance(datetime_input, str)
        else datetime_input
    )
    if not dt:
        raise ValueError("Invalid datetime input")
    dt += timedelta(hours=1)
    return dt.strftime("%Y-%m-%d")


def parse_date(date_input):
    # Convert date to string
    val = str(date_input)
    parsed_date = datetime.fromisoformat(val)
    day = parsed_date.strftime("%d").lstrip("0")  # Remove leading zero
    month = parsed_date.strftime("%b.")
    year = parsed_date.strftime("%Y")

    # Add appropriate suffix to the day
    if day.endswith("1") and day != "11":
        suffix = "st"
    elif day.endswith("2") and day != "12":
        suffix = "nd"
    elif day.endswith("3") and day != "13":
        suffix = "rd"
    else:
        suffix = "th"

    formatted_date = f"{month} {day}{suffix} {year}"
    return formatted_date


def split_full_name(full_name: str) -> tuple[str, str]:
    """
    Splits a full name into first name and last name.

    If only one name is provided, the last name will be an empty string.

    Args:
        full_name (str): The user's full name.

    Returns:
        tuple: (first_name, last_name)
    """
    name = full_name.strip()
    if not name:
        return "", ""

    parts = name.split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def custom_flatten_uuid(uuid_string):
    """Flatten a UUID string by removing dashes and reverses the string."""
    return uuid_string.replace("-", "")[::-1]


def unflatten_uuid(flattened_uuid):
    flattened_uuid = flattened_uuid[::-1]
    """Deflatten a flattened UUID string by reversing the string and adding dashes."""
    return "-".join(
        [
            flattened_uuid[:8],
            flattened_uuid[8:12],
            flattened_uuid[12:16],
            flattened_uuid[16:20],
            flattened_uuid[20:],
        ]
    )


def add_commas_to_transaction_amount(number):
    number = str(number)
    # Round the number to 2 decimal places
    number = round(float(number), 2)
    # Split the number into integer and decimal parts
    integer_part, decimal_part = str(number).split(".")
    # Reverse the integer part
    reversed_int = integer_part[::-1]
    # Initialize variables
    result = ""
    count = 0
    # Iterate through the reversed string
    for char in reversed_int:
        result = char + result
        count += 1
        # Add comma after every third character, except for the last group
        if count % 3 == 0 and count != len(reversed_int):
            result = "," + result
    # Add the decimal part back, ensuring it has 2 digits
    result = f"{result}.{decimal_part.zfill(2)}"
    return result


def convert_to_camel(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def generate_temp_id():
    return str(uuid4())


def generate_short_uuid():
    new_uuid = generate_temp_id()
    return new_uuid.split("-")[0][:-4] + generate_random_text(20)


api_key_prefix = (
    "live" if os.environ.get("ENVIRONMENT", None) == "production" else "test"
)


def get_pub_key():
    return "{}_{}".format(f"{api_key_prefix}_pub", generate_short_uuid())


def get_priv_key():
    return "{}_{}".format(f"{api_key_prefix}_priv", generate_short_uuid())


def generate_otp():
    return str(random.randint(100000, 999999))


def replace_space(file_name):
    return file_name.replace(" ", "_")


def minutes_to_seconds(minutes):
    return minutes * 60


def hours_to_seconds(hours):
    return minutes_to_seconds(hours * 60)


def days_to_seconds(days):
    return hours_to_seconds(days * 24)


def get_lga_by_state_alias(lga_map, state_alias):
    return lga_map.get(state_alias, None)


def generate_random_text(length):
    return "".join(
        random.choice("0123456789abcdefghijklmnopqrstuvwxyz") for i in range(length)
    )

def capitalize_fields_decorator(fields_to_capitalize=None):
    """
    Decorator to capitalize specific fields in the serialized representation.
    Defaults to capitalizing 'name' if no fields are specified.

    Args:
    fields_to_capitalize (list): List of field names to capitalize.
    """
    if fields_to_capitalize is None:
        fields_to_capitalize = ["name"]  # Default to 'name'

    def decorator(serializer_class):
        original_to_representation = serializer_class.to_representation

        def new_to_representation(self, instance):
            # Call the original method
            representation = original_to_representation(self, instance)

            # Capitalize specified fields
            for field in fields_to_capitalize:
                if field in representation and representation[field]:
                    representation[field] = representation[field].upper()

            return representation        # Override the serializer's to_representation method with the new one
        serializer_class.to_representation = new_to_representation
        return serializer_class

    return decorator


# Email provider constants
EMAIL_SMTP_PROVIDERS = ["SENDGRID", "AWS_SES"]
