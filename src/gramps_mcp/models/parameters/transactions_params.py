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
Parameters for transactions endpoints.
"""

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class TransactionHistoryParams(BaseModel):
    """
    Parameters for getting transaction history.

    Note: This endpoint supports page/pagesize for pagination but does NOT
    support other BaseGetMultipleParams fields like gramps_id, profile, extend, gql, backlinks.
    
    Parameters:
        old (Optional[bool]): Whether to include the raw object data before the change
        new (Optional[bool]): Whether to include the raw object data after the change
        page (Optional[int]): Page number for pagination (default: 0)
        pagesize (Optional[int]): Number of records per page (default: 20)
        before (Optional[float]): Unix timestamp. Only return transactions committed before this time
        after (Optional[float]): Unix timestamp. Only return transactions committed after this time
        sort (Optional[str]): Field to sort by (e.g., '-id' for descending)

    Returns:
        Dict[str, Any]: List of transaction history
    """

    @field_validator("page", mode="before")
    @classmethod
    def coerce_page(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce page to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("pagesize", mode="before")
    @classmethod
    def coerce_pagesize(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce pagesize to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("old", mode="before")
    @classmethod
    def coerce_old(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce old to bool."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("new", mode="before")
    @classmethod
    def coerce_new(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce new to bool."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("before", mode="before")
    @classmethod
    def coerce_before(cls, v: Union[float, int, str, None]) -> Optional[float]:
        """Coerce before to float."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return float(v)
        return float(v) if v is not None else None

    @field_validator("after", mode="before")
    @classmethod
    def coerce_after(cls, v: Union[float, int, str, None]) -> Optional[float]:
        """Coerce after to float."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return float(v)
        return float(v) if v is not None else None

    old: Optional[bool] = Field(
        None, description="Whether to include the raw object data before the change"
    )
    new: Optional[bool] = Field(
        None, description="Whether to include the raw object data after the change"
    )
    page: Optional[int] = Field(
        None, ge=0, description="Page number for pagination (default: 0)"
    )
    pagesize: Optional[int] = Field(
        None, gt=0, description="Number of records per page (default: 20)"
    )
    before: Optional[float] = Field(
        None,
        description="Unix timestamp. Only return transactions committed before this time",
    )
    after: Optional[float] = Field(
        None,
        description="Unix timestamp. Only return transactions committed after this time",
    )
    sort: Optional[str] = Field(
        None, description="Field to sort by (e.g., '-id' for descending)"
    )


class TransactionHistoryByIdParams(BaseModel):
    """
    Parameters for getting specific transaction history.

    Args:
        transaction_id (int): ID of the transaction to get details for
        old (Optional[bool]): Whether to include the raw object data before the change
        new (Optional[bool]): Whether to include the raw object data after the change

    Returns:
        Dict[str, Any]: Transaction details
    """

    transaction_id: int = Field(
        ..., description="ID of the transaction to get details for"
    )
    old: Optional[bool] = Field(
        None, description="Whether to include the raw object data before the change"
    )
    new: Optional[bool] = Field(
        None, description="Whether to include the raw object data after the change"
    )
