# gramps-mcp - AI-Powered Genealogy Research & Management
# Copyright (C) 2025 cabout.me
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Core data type models for Gramps API definitions.

This module contains basic type definitions used throughout the Gramps API,
including Date, Name, Surname, Attribute, Address, Location, URL, and styled text models.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Date(BaseModel):
    """
    Represents a date in various formats and qualities.

    Attributes:
        calendar: The calendar format for the date (typically 0 for Julian).
        dateval: A mixed array representing the date value (year, month, day, etc.).
        format: The format string for the date.
        modifier: Date modifier indicator.
        newyear: When new year begins in this calendar.
        quality: Quality indicator for the date (estimated, calculated, etc.).
        sortval: Integer value to use for date sorting.
        text: Textual representation of the date.
        year: The year component of the date.
    """

    calendar: Optional[int] = Field(None, description="The calendar format for the date.")
    dateval: Optional[List[object]] = Field(None, description="The value for the date. A mixed array of integer and boolean types.")
    format: Optional[str] = Field(None, description="The format for the date.")
    modifier: Optional[int] = Field(None, description="Modifier.")
    newyear: Optional[int] = Field(None, description="New year begins.")
    quality: Optional[int] = Field(None, description="Quality.")
    sortval: Optional[int] = Field(None, description="Value to use for date sorting.")
    text: Optional[str] = Field(None, description="Textual representation of the date.")
    year: Optional[int] = Field(None, description="Year.")


class Surname(BaseModel):
    """
    Represents a surname with modifiers and origin information.

    Attributes:
        connector: Connector to tie given name and surname together.
        origintype: The origin/type of the name.
        prefix: A name prefix (e.g., "von", "de").
        primary: Whether this is the primary surname.
        surname: The actual surname string.
    """

    connector: Optional[str] = Field(None, description="Connector to tie given name and surname together.")
    origintype: Optional[str] = Field(None, description="Name origin.")
    prefix: Optional[str] = Field(None, description="A name prefix.")
    primary: Optional[bool] = Field(None, description="Primary surname indicator.")
    surname: Optional[str] = Field(None, description="Actual surname.")


class Name(BaseModel):
    """
    Represents a person's name with all its components.

    Attributes:
        call: Call name.
        citation_list: Handles for citations supporting the name.
        date: Date the name was in use.
        display_as: Identifier for how to display the name.
        famnick: Family nickname.
        first_name: First part of name (given name).
        group_as: For identifying how to group the name.
        nick: Nickname.
        note_list: Handles for research notes about the name.
        private: Whether this record is private.
        sort_as: For identifying how to sort the name.
        suffix: Suffix, usually denotes credentials.
        surname_list: List of surnames.
        title: Prefix or title.
        type: Type of name (e.g., "Birth Name", "Married Name").
    """

    call: Optional[str] = Field(None, description="Call name.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the name.")
    date: Optional[Date] = Field(None, description="Date the name was in use.")
    display_as: Optional[int] = Field(None, description="Identifier for how to display the name.")
    famnick: Optional[str] = Field(None, description="Family nickname.")
    first_name: Optional[str] = Field(None, description="First part of name.")
    group_as: Optional[str] = Field(None, description="For identifying how to group the name.")
    nick: Optional[str] = Field(None, description="Nickname.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the name.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    sort_as: Optional[int] = Field(None, description="For identifying how to sort the name.")
    suffix: Optional[str] = Field(None, description="Suffix, usually denotes credentials.")
    surname_list: Optional[List[Surname]] = Field(None, description="Surnames.")
    title: Optional[str] = Field(None, description="Prefix or title.")
    type: Optional[str] = Field(None, description="Type of name.")


class Attribute(BaseModel):
    """
    Represents an attribute of a genealogical object.

    Attributes:
        citation_list: Handles for citations supporting the attribute.
        note_list: Handles for research notes about the attribute.
        private: Whether this record is private.
        type: Type of the attribute (e.g., "Social Security Number").
        value: Value of the attribute.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the attribute.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the attribute.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    type: Optional[str] = Field(None, description="Type of the attribute.")
    value: Optional[str] = Field(None, description="Value of the attribute.")


class Address(BaseModel):
    """
    Represents a physical address.

    Attributes:
        citation_list: Handles for citations supporting the address.
        city: City name.
        country: Country name.
        county: County name.
        date: Date resident at the address.
        locality: Locality name.
        note_list: Handles for research notes about the address.
        phone: Phone number.
        postal: Postal code.
        private: Whether this record is private.
        state: State/province name.
        street: Street address.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the address.")
    city: Optional[str] = Field(None, description="City.")
    country: Optional[str] = Field(None, description="Country.")
    county: Optional[str] = Field(None, description="County.")
    date: Optional[Date] = Field(None, description="Date resident at the address.")
    locality: Optional[str] = Field(None, description="Locality.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the address.")
    phone: Optional[str] = Field(None, description="Phone number.")
    postal: Optional[str] = Field(None, description="Postal code.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    state: Optional[str] = Field(None, description="State.")
    street: Optional[str] = Field(None, description="Street.")


class Location(BaseModel):
    """
    Represents a geographic location (similar to Address but without dates/citations).

    Attributes:
        city: City name.
        country: Country name.
        county: County name.
        locality: Locality name.
        parish: Parish name.
        phone: Phone number.
        postal: Postal code.
        state: State/province name.
        street: Street address.
    """

    city: Optional[str] = Field(None, description="City.")
    country: Optional[str] = Field(None, description="Country.")
    county: Optional[str] = Field(None, description="County.")
    locality: Optional[str] = Field(None, description="Locality.")
    parish: Optional[str] = Field(None, description="Parish.")
    phone: Optional[str] = Field(None, description="Phone number.")
    postal: Optional[str] = Field(None, description="Postal code.")
    state: Optional[str] = Field(None, description="State.")
    street: Optional[str] = Field(None, description="Street.")


class URL(BaseModel):
    """
    Represents a URL/web link with descriptive information.

    Attributes:
        desc: Description of the URL.
        path: The URL itself.
        private: Whether this record is private.
        type: Type of URL (e.g., "Web Home", "Email").
    """

    desc: Optional[str] = Field(None, description="Description of the URL.")
    path: Optional[str] = Field(None, description="URL.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    type: Optional[str] = Field(None, description="Type of URL.")


class StyledTextTag(BaseModel):
    """
    Represents a formatting tag in styled text.

    Attributes:
        name: Name of the tag (e.g., "Bold", "Italic").
        value: Value of the tag (can be null, string, or integer).
        ranges: Ranges in the text where this tag applies.
    """

    name: Optional[str] = Field(None, description="Name of the tag.")
    value: Optional[object] = Field(None, description="Value of the tag. Note type may be null, string, or integer.")
    ranges: Optional[List[int]] = Field(None, description="Ranges.")


class StyledText(BaseModel):
    """
    Represents text with styling and formatting tags.

    Attributes:
        string: The text content itself.
        tags: List of formatting tags applied to the text.
    """

    string: Optional[str] = Field(None, description="The text itself.")
    tags: Optional[List[StyledTextTag]] = Field(None, description="The text tags.")


class Span(BaseModel):
    """
    Represents a period of elapsed time.

    Attributes:
        span: A human-readable description of a period of elapsed time.
    """

    span: Optional[str] = Field(None, description="A description of a period of elapsed time.")
