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
Parameters for task management operations.

API calls supported in this category:
- GET_TASK_STATUS: Get the status of an async task
"""

from pydantic import BaseModel, Field


class TaskStatusParams(BaseModel):
    """
    Parameters for getting task status.

    Args:
        task_id (str): The ID of the task to check
    """

    task_id: str = Field(..., description="The ID of the task to check")
