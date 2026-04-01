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
    Represents a date in various calendar formats with quality and modifier information.

    Gramps supports multiple calendar systems and allows dates to carry quality
    (estimated/calculated) and modifier (before/after/about/range/span) indicators
    to express uncertainty, time ranges, or researcher inferences.

    Attributes:
        calendar: Calendar system identifier. 0=Gregorian (default), 1=Julian, 2=Hebrew,
            3=French Republican, 4=Persian, 5=Islamic, 6=Swedish.
        dateval: Raw date array [day, month, year, is_slash]. Day/month=0 when unknown.
            Example: [25, 12, 1900, False] = 25 December 1900. Range dates use two sub-arrays.
        format: Display format string; system-controlled. Leave null when creating dates.
        modifier: Date modifier. 0=exact, 1=before, 2=after, 3=about/circa,
            4=range (from...to), 5=span (between...and), 6=text-only (no structured date).
        newyear: New-year start offset. 0=calendar default, 1=January 1, 2=March 25.
            Relevant for pre-Gregorian historical dates.
        quality: Date accuracy indicator. 0=as-recorded, 1=estimated (researcher inference),
            2=calculated (derived arithmetically, e.g. birth year from age at census).
        sortval: Auto-computed integer for chronological sorting. Read-only; set by system.
        text: Free-form textual date. Examples: 'circa 1900', 'Summer 1875', 'before 1800'.
            Primary content when modifier=6; supplementary label otherwise.
        year: Year component as integer. Examples: 1900, 1776, 1066.
    """

    calendar: Optional[int] = Field(None, description="Calendar system: 0=Gregorian (default), 1=Julian, 2=Hebrew, 3=French Republican, 4=Persian, 5=Islamic, 6=Swedish.")
    dateval: Optional[List[object]] = Field(None, description="Raw date array [day, month, year, is_slash]. Example: [25, 12, 1900, False] = 25 Dec 1900. Day/month=0 for unknown component.")
    format: Optional[str] = Field(None, description="Display format string; system-controlled. Leave null when creating dates.")
    modifier: Optional[int] = Field(None, description="Date modifier: 0=exact, 1=before, 2=after, 3=about/circa, 4=range (from-to), 5=span (between-and), 6=text-only.")
    newyear: Optional[int] = Field(None, description="New-year start offset: 0=calendar default, 1=January 1, 2=March 25. Relevant for pre-Gregorian historical dates.")
    quality: Optional[int] = Field(None, description="Date accuracy: 0=as-recorded, 1=estimated (researcher inference), 2=calculated (derived arithmetically).")
    sortval: Optional[int] = Field(None, description="Auto-computed chronological sort integer. Read-only; set by the system.")
    text: Optional[str] = Field(None, description="Free-form textual date. Examples: 'circa 1900', 'Summer 1875', 'before 1800'. Required when modifier=6 (text-only).")
    year: Optional[int] = Field(None, description="Year component. Examples: 1900, 1776, 1066.")


class Surname(BaseModel):
    """
    Represents one surname component in a person's full name.

    A person may have multiple surnames in a surname_list (e.g., double-barreled names,
    patronymics, or matronymics). Each Surname carries prefix, origin type, and connector
    metadata. Only one surname should be marked as primary.

    Attributes:
        connector: Conjunction linking this surname to the next. Examples: '', 'and', 'y'.
            Empty string means surnames are concatenated with no joining word.
        origintype: Linguistic or cultural origin of this surname. Examples: 'Inherited',
            'Given', 'Taken', 'Patronymic', 'Matronymic', 'Feudal', 'Pseudonym',
            'Patrilineal', 'Matrilineal', 'Occupation', 'Location', 'Unknown', 'Other'.
        prefix: Surname prefix/particle. Examples: 'von', 'de', 'van der', 'le', 'Mac'.
            Empty string if no prefix.
        primary: True if this is the primary/canonical surname used for sorting and display.
            Exactly one surname per Name should be primary.
        surname: The surname string. Examples: 'Smith', 'Müller', 'García', "O'Brien".
    """

    connector: Optional[str] = Field(None, description="Conjunction linking multiple surnames. Examples: '', 'and', 'y'. Empty string = surnames concatenated with no joining word.")
    origintype: Optional[str] = Field(None, description="Surname origin type. Examples: 'Inherited', 'Patronymic', 'Matronymic', 'Given', 'Pseudonym', 'Occupation', 'Location', 'Unknown'.")
    prefix: Optional[str] = Field(None, description="Surname prefix/particle. Examples: 'von', 'de', 'van der', 'le', 'Mac'. Empty string if no prefix.")
    primary: Optional[bool] = Field(None, description="True if this is the primary/canonical surname for sorting and display. Exactly one surname per Name should be primary.")
    surname: Optional[str] = Field(None, description="Surname string. Examples: 'Smith', 'Müller', 'García', \"O'Brien\".")


class Name(BaseModel):
    """
    Represents a complete name record for a person with all components and metadata.

    Names carry their type (birth, married, etc.), all name components (given name,
    surname list, title, suffix), citation/note support, and date range indicating
    when the name was in use. A person can have multiple Name entries.

    Attributes:
        call: Name the person is commonly called, often a middle name used instead of first.
            Example: 'Robert' for a person named 'John Robert Smith' who goes by Robert.
        citation_list: Handles for citations supporting this name record.
        date: Date or range when this name was in use. Tracks maiden names, married names,
            or name changes over time.
        display_as: Integer (0-6) selecting the name display format pattern.
        famnick: Family/household nickname applying to the whole household.
            Example: 'The Maryland Smiths' to distinguish from other Smith branches.
        first_name: Given/first name(s). Examples: 'John', 'Mary Ann', 'José Maria'.
        group_as: Override for surname grouping index. Normalizes spelling variants.
            Example: 'Mueller' as grouping for 'Müller' to keep variants together.
        nick: Personal nickname. Examples: 'Skip', 'Bud', 'Mimi', 'Doc'.
        note_list: Handles for research notes about this name.
        private: True if this name record is confidential and should not be published.
        sort_as: Integer (0-13) selecting the sort-order format for this name.
        suffix: Name suffix denoting generation or credentials.
            Examples: 'Jr.', 'Sr.', 'III', 'M.D.', 'Ph.D.'.
        surname_list: List of Surname components. May be multiple for compound surnames
            or cultures with multiple surnames (e.g. Spanish double surnames).
        title: Name title or honorific. Examples: 'Dr.', 'Rev.', 'Sir', 'Mrs.', 'Col.'.
        type: Name category. Examples: 'Birth Name', 'Married Name', 'Also Known As',
            'Alternate Name', 'Name Change', 'Nickname', 'Unknown'.
    """

    call: Optional[str] = Field(None, description="Name the person is commonly called, often a middle name. Example: 'Robert' for 'John Robert Smith' who goes by Robert.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this name record.")
    date: Optional[Date] = Field(None, description="Date or range when this name was in use. Tracks maiden names, married names, and name changes.")
    display_as: Optional[int] = Field(None, description="Integer (0-6) selecting the name display format pattern.")
    famnick: Optional[str] = Field(None, description="Family/household nickname. Example: 'The Maryland Smiths' to distinguish from other Smith branches.")
    first_name: Optional[str] = Field(None, description="Given/first name(s). Examples: 'John', 'Mary Ann', 'José Maria'.")
    group_as: Optional[str] = Field(None, description="Override for surname grouping index. Normalizes spelling variants. Example: 'Mueller' grouping for 'Müller'.")
    nick: Optional[str] = Field(None, description="Personal nickname. Examples: 'Skip', 'Bud', 'Mimi', 'Doc'.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this name.")
    private: Optional[bool] = Field(None, description="True if this name record is confidential and should not be published.")
    sort_as: Optional[int] = Field(None, description="Integer (0-13) selecting the sort-order format for this name.")
    suffix: Optional[str] = Field(None, description="Name suffix. Examples: 'Jr.', 'Sr.', 'III', 'M.D.', 'Ph.D.'.")
    surname_list: Optional[List[Surname]] = Field(None, description="List of Surname components. May be multiple for compound or double surnames.")
    title: Optional[str] = Field(None, description="Name title or honorific. Examples: 'Dr.', 'Rev.', 'Sir', 'Mrs.', 'Col.', 'Prof.'.")
    type: Optional[str] = Field(None, description="Name category. Examples: 'Birth Name', 'Married Name', 'Also Known As', 'Alternate Name', 'Name Change', 'Nickname'.")


class Attribute(BaseModel):
    """
    Represents a key-value attribute (additional typed property) of a genealogical object.

    Attributes store extra properties that don't fit standard fields, such as occupations,
    identification numbers, physical descriptions, or custom research data.

    Attributes:
        citation_list: Handles for citations supporting this attribute's value.
        note_list: Handles for research notes about this attribute.
        private: True if this attribute is confidential.
        type: Attribute type/category. Examples: 'Occupation', 'Age', 'Cause of Death',
            'Description', 'Education', 'ID Number', 'Medical Information', 'National Origin',
            'Number of Marriages', 'Residence', 'Social Security Number', 'Web Home'.
        value: Attribute value string. Examples: 'Farmer', '45', 'Tuberculosis',
            'High school graduate', '123-45-6789', 'Boston, Massachusetts'.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this attribute.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this attribute.")
    private: Optional[bool] = Field(None, description="True if this attribute is confidential.")
    type: Optional[str] = Field(None, description="Attribute type. Examples: 'Occupation', 'Age', 'Cause of Death', 'Social Security Number', 'Education', 'Residence', 'Description'.")
    value: Optional[str] = Field(None, description="Attribute value. Examples: 'Farmer', '45', 'Tuberculosis', 'High school graduate', '123-45-6789'.")


class Address(BaseModel):
    """
    Represents a physical address with an associated time period.

    Used to record where a person or repository was located during a specific period.
    The date field indicates when the person resided at or was associated with this address.

    Attributes:
        citation_list: Handles for citations supporting this address record.
        city: City name. Examples: 'Boston', 'London', 'München', 'New York City'.
        country: Country name. Examples: 'USA', 'United Kingdom', 'Germany', 'France'.
        county: County or administrative district. Examples: 'Suffolk County', 'Kent', 'Bavaria'.
        date: Date or period when resident at this address.
        locality: Sub-city locality or neighborhood. Examples: 'Brooklyn', 'Southwark', 'Mitte'.
        note_list: Handles for research notes about this address.
        phone: Phone number in any format. Examples: '+1-555-123-4567', '020 7946 0958'.
        postal: Postal or ZIP code. Examples: '02101', 'SW1A 1AA', '80331'.
        private: True if this address record is confidential.
        state: State, province, or region. Examples: 'Massachusetts', 'California', 'Bavaria'.
        street: Street address line. Examples: '123 Main Street', '10 Downing Street Apt 2'.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this address.")
    city: Optional[str] = Field(None, description="City name. Examples: 'Boston', 'London', 'München', 'New York City'.")
    country: Optional[str] = Field(None, description="Country name. Examples: 'USA', 'United Kingdom', 'Germany', 'France'.")
    county: Optional[str] = Field(None, description="County or administrative district. Examples: 'Suffolk County', 'Kent', 'Bavaria', 'Middlesex'.")
    date: Optional[Date] = Field(None, description="Date or period when resident at this address.")
    locality: Optional[str] = Field(None, description="Sub-city locality or neighborhood. Examples: 'Brooklyn', 'Southwark', 'Mitte'.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this address.")
    phone: Optional[str] = Field(None, description="Phone number. Examples: '+1-555-123-4567', '020 7946 0958'.")
    postal: Optional[str] = Field(None, description="Postal or ZIP code. Examples: '02101', 'SW1A 1AA', '80331'.")
    private: Optional[bool] = Field(None, description="True if this address record is confidential.")
    state: Optional[str] = Field(None, description="State, province, or region. Examples: 'Massachusetts', 'California', 'Bavaria', 'Ontario'.")
    street: Optional[str] = Field(None, description="Street address line. Examples: '123 Main Street', '10 Downing Street Apt 2'.")


class Location(BaseModel):
    """
    Represents a geographic location without date or citation metadata.

    Similar to Address but used in contexts where temporal and evidentiary metadata
    is not needed (e.g., alternate locations for a Place record). Lacks date,
    citation_list, note_list, and private fields compared to Address.

    Attributes:
        city: City name. Examples: 'Springfield', 'Dresden', 'Lyon'.
        country: Country name. Examples: 'USA', 'Germany', 'France', 'Poland'.
        county: County or administrative district. Examples: 'Greene County', 'Saxony', 'Kent'.
        locality: Sub-city locality. Examples: 'Downtown', 'Old Town', 'Eastside'.
        parish: Parish name, common in British and European genealogy records.
            Examples: 'St. Mary Abchurch', 'Parish of Chelmsford', 'St. John the Baptist'.
        phone: Phone number associated with the location.
        postal: Postal or ZIP code. Examples: '62701', '01067', '69001'.
        state: State, province, or region. Examples: 'Illinois', 'Saxony', 'Ontario'.
        street: Street address line. Examples: '15 Elm Street', 'Königstraße 12'.
    """

    city: Optional[str] = Field(None, description="City name. Examples: 'Springfield', 'Dresden', 'Lyon'.")
    country: Optional[str] = Field(None, description="Country name. Examples: 'USA', 'Germany', 'France', 'Poland'.")
    county: Optional[str] = Field(None, description="County or administrative district. Examples: 'Greene County', 'Saxony', 'Kent'.")
    locality: Optional[str] = Field(None, description="Sub-city locality. Examples: 'Downtown', 'Old Town', 'Eastside'.")
    parish: Optional[str] = Field(None, description="Parish name. Examples: 'St. Mary Abchurch', 'Parish of Chelmsford', 'St. John the Baptist'.")
    phone: Optional[str] = Field(None, description="Phone number associated with the location.")
    postal: Optional[str] = Field(None, description="Postal or ZIP code. Examples: '62701', '01067', 'SW1A 1AA'.")
    state: Optional[str] = Field(None, description="State, province, or region. Examples: 'Illinois', 'Saxony', 'Auvergne-Rhône-Alpes'.")
    street: Optional[str] = Field(None, description="Street address line. Examples: '15 Elm Street', 'Königstraße 12'.")


class URL(BaseModel):
    """
    Represents a URL or web link associated with a genealogical object.

    URLs link to online resources about a person, family, place, source, or repository.
    Each URL record has a type category, human-readable description, and the URL path.

    Attributes:
        desc: Human-readable description of the link. Examples: 'Wikipedia article',
            'FindAGrave memorial', 'Ancestry.com profile', 'Official website'.
        path: The URL string itself. Examples: 'https://www.findagrave.com/memorial/12345',
            'https://en.wikipedia.org/wiki/John_Smith', 'mailto:contact@example.com'.
        private: True if this URL record is confidential.
        type: URL category. Examples: 'Web Home', 'Web Search', 'FTP', 'Email'.
    """

    desc: Optional[str] = Field(None, description="Human-readable link description. Examples: 'Wikipedia article', 'FindAGrave memorial', 'Official website', 'Ancestry.com profile'.")
    path: Optional[str] = Field(None, description="URL string. Examples: 'https://www.findagrave.com/memorial/12345', 'https://en.wikipedia.org/wiki/Example', 'mailto:info@example.com'.")
    private: Optional[bool] = Field(None, description="True if this URL record is confidential.")
    type: Optional[str] = Field(None, description="URL category. Examples: 'Web Home', 'Web Search', 'FTP', 'Email'.")


class StyledTextTag(BaseModel):
    """
    Represents a formatting tag applied to a character range within styled text.

    Tags define visual formatting or structural markup for portions of Note text content.
    Each tag identifies a format type, optional parameter (for parameterized styles such
    as font name or link URL), and the character ranges where the formatting applies.

    Attributes:
        name: Formatting type identifier. Integer values: 0='Bold', 1='Italic',
            2='Underline', 3='Fontface', 4='Fontsize', 5='Fontcolor', 6='Highlight',
            7='Superscript', 8='Link'.
        value: Format parameter. Null for simple styles (Bold/Italic/Underline).
            String for link URLs or font face names. Integer for font sizes in points.
            Examples: 'https://example.com' (link), 'Arial' (fontface), 14 (fontsize).
        ranges: Character range pairs [[start, end], ...] indicating where formatting applies.
            Example: [[0, 5], [10, 15]] = applies to characters 0-4 and 10-14.
    """

    name: Optional[str] = Field(None, description="Formatting type. Integer values: 0='Bold', 1='Italic', 2='Underline', 3='Fontface', 4='Fontsize', 5='Fontcolor', 6='Highlight', 7='Superscript', 8='Link'.")
    value: Optional[object] = Field(None, description="Format parameter. Null for simple styles. String for link URLs or font names. Integer for font size in points. Examples: 'https://example.com', 'Arial', 14.")
    ranges: Optional[List[int]] = Field(None, description="Character range pairs [[start,end],...] where format applies. Example: [[0,5],[10,15]] applies to chars 0-4 and 10-14.")


class StyledText(BaseModel):
    """
    Represents text content with optional inline formatting tags.

    Used for Note content that may contain rich text formatting such as bold, italic,
    hyperlinks, and font changes applied over character ranges.

    Attributes:
        string: The plain text content. The displayable text of the note before
            any formatting is applied. This is also what full-text search operates on.
        tags: List of StyledTextTag objects defining formatting applied over character
            ranges within string. Empty list or null if the note is plain text.
    """

    string: Optional[str] = Field(None, description="Plain text content. The displayable text of the note before formatting is applied.")
    tags: Optional[List[StyledTextTag]] = Field(None, description="List of formatting tags (bold, italic, links, font changes) applied over character ranges. Null or empty for plain text.")


class Span(BaseModel):
    """
    Represents a human-readable elapsed time span between two dates.

    Used in profile summaries to convey durations such as a person's age at death
    or the length of a marriage. Formatted as a natural language string by the API.

    Attributes:
        span: Human-readable elapsed time description.
            Examples: '32 years, 4 months, 12 days', '1 year', '6 months', '3 days'.
    """

    span: Optional[str] = Field(None, description="Human-readable elapsed time. Examples: '32 years, 4 months, 12 days', '1 year', '6 months', '3 days'.")
