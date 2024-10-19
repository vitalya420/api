from enum import Enum

from sanic_ext.extensions.openapi import openapi


@openapi.component
class Realm(str, Enum):
    """
    Enum representing the different realms of application access.

    This Enum defines the various contexts in which an application can operate.
    Each member of the Enum corresponds to a specific realm:

    - `web`: Represents access through a web application.
    - `mobile`: Represents access through a mobile application.

    The `Realm` class inherits from both `str` and `Enum`, allowing its members to be used as strings
    while also providing the benefits of an enumeration.

    Usage:
        To access a specific realm, you can use:

        ```python
        current_realm = Realm.web
        ```

    Attributes:
        web (str): The string representation for the web realm.
        mobile (str): The string representation for the mobile realm.
    """

    web = "web"
    mobile = "mobile"


@openapi.component
class NewsContentType(str, Enum):
    plain = "plain"
    html = "html"
    markdown = "markdown"


@openapi.component
class Currency(str, Enum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"


class AuthMethod(str, Enum):
    password = "password"
    otp = "otp"


class DayOfWeek(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"
