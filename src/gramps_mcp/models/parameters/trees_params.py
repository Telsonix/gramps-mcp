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
Parameters for tree management operations.

API calls supported in this category:
- GET_TREES: List all family trees
- GET_TREE: Get details of a specific family tree
"""

from typing import Optional

from pydantic import BaseModel, Field


class TreesListParams(BaseModel):
    """
    Parameters for listing all family trees.

    No parameters required - returns all available trees.
    """
    pass


class TreeDetailsParams(BaseModel):
    """
    Parameters for getting details of a specific tree.

    Args:
        tree_id (str): The ID of the tree to get details for
    """

    tree_id: str = Field(..., description="The ID of the tree")


class HolidaysListParams(BaseModel):
    """
    Parameters for getting holidays for a specific country and year.

    Args:
        country (str): The country code (default: 'US')
        year (Optional[int]): The year (default: current year)
    """

    country: str = Field("US", description="Country code (default: 'US')")
    year: Optional[int] = Field(
        None, description="Year for holidays (default: current year)"
    )


class ReportListParams(BaseModel):
    """
    Parameters for listing all available reports.

    No parameters required - returns all available reports.
    """

    pass


class ReportDetailsParams(BaseModel):
    """
    Parameters for getting details of a specific report.

    Args:
        report_id (str): The ID of the report
    """

    report_id: str = Field(..., description="The ID of the report")


class ReportFileDownloadParams(BaseModel):
    """
    Parameters for downloading a report file.

    Args:
        report_id (str): The ID of the report
    """

    report_id: str = Field(..., description="The ID of the report")


class SubmitReportParams(BaseModel):
    """
    Parameters for submitting a report file for generation.

    Args:
        report_id (str): The ID of the report
        options (Optional[str]): Report options in JSON format
    """

    report_id: str = Field(..., description="The ID of the report")
    options: str = Field(
        "{}",
        description="Report options as JSON string (e.g., '{\"pid\": \"I0001\"}')",
    )


class ProcessedReportParams(BaseModel):
    """
    Parameters for getting a processed report file.

    Args:
        report_id (str): The ID of the report
        filename (str): The filename of the processed report
    """

    report_id: str = Field(..., description="The ID of the report")
    filename: str = Field(..., description="The filename of the processed report")
