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
Parameters for DNA matching operations.

API calls supported in this category:
- GET_PERSON_DNA_MATCHES: Get DNA matches for a person
- POST_PARSERS_DNA_MATCH: Submit DNA match file for parsing
"""

from typing import Optional

from pydantic import BaseModel, Field


class DNAMatchesParams(BaseModel):
    """
    Parameters for getting DNA matches for a person.

    Args:
        gramps_id (str): The Gramps ID of the person to get matches for
    """

    gramps_id: str = Field(..., description="The Gramps ID of the person")


class DnaParserParams(BaseModel):
    """
    Parameters for submitting a DNA match file for parsing.

    Args:
        file_path (str): Path to the DNA match file
        file_format (Optional[str]): Format of the file (e.g., 'gedcom', 'dna')
    """

    file_path: str = Field(..., description="Path to the DNA match file")
    file_format: Optional[str] = Field(
        "gedcom", description="Format of the DNA file (default: gedcom)"
    )
