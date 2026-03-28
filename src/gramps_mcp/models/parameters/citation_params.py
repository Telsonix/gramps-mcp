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
Pydantic models for citation-related operations.

API calls supported in this category:
- GET_CITATIONS: Get information about multiple citations
- POST_CITATIONS: Add a new citation to the database
- GET_CITATION: Get information about a specific citation
- PUT_CITATION: Update the citation
- DELETE_CITATION: Delete the citation
"""

from typing import Any, Dict, Optional, Union

from pydantic import Field, field_validator

from .base_params import BaseDataModel, BaseGetMultipleParams
from .event_params import _coerce_date


class GetCitationsParams(BaseGetMultipleParams):
    """Parameters for GET /citations endpoint."""

    dates: Optional[str] = Field(
        None, description="A date filter that operates on the citation date."
    )


class CitationData(BaseDataModel):
    """Model for creating or updating a citation via POST/PUT endpoints."""

    date: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        description=(
            "Citation date. Plain string ('1850', '1850-06', '1850-06-15') "
            "or full Gramps Date object."
        ),
    )
    page: Optional[str] = Field(None, description="Page or location within the source")
    source_handle: str = Field(..., description="Handle of the source being cited")

    @field_validator("date", mode="before")
    @classmethod
    def coerce_date(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Accept plain date strings and convert to Gramps Date object."""
        return _coerce_date(v)
