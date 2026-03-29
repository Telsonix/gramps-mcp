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
Family data handler for Gramps MCP operations.

Provides clean, direct formatting of family data from handles.
"""

import logging

from ..models.api_calls import ApiCalls
from .date_handler import format_date
from .place_handler import format_place

logger = logging.getLogger(__name__)


async def format_family(client, tree_id: str, handle: str) -> str:
    """
    Format family data with members and basic details.

    Args:
        client: Gramps API client instance
        tree_id (str): Family tree identifier
        handle (str): Family handle

    Returns:
        str: Formatted family string with members and details
    """
    if not handle:
        return "• **Family**\n  No handle provided\n\n"

    try:
        # Get family data with extended information
        family_data = await client.make_api_call(
            ApiCalls.GET_FAMILY,
            tree_id=tree_id,
            handle=handle,
            params={"extend": "all"},
        )
        if not family_data:
            return f"• **Family {handle}**\n  Family not found\n\n"

        gramps_id = family_data.get("gramps_id", "")
        result = ""

        # First line: Father: Name (Gender) - ID | Mother: Name (Gender) - ID
        # - FamilyID - [family_handle]
        family_members = []

        # Get father
        father_handle = family_data.get("father_handle", "")
        if father_handle:
            try:
                father_data = await client.make_api_call(
                    ApiCalls.GET_PERSON, tree_id=tree_id, handle=father_handle
                )
                if father_data:
                    father_name = _extract_person_name(father_data)
                    father_gender = _get_gender_letter(father_data.get("gender", 2))
                    father_id = father_data.get("gramps_id", "")
                    family_members.append(
                        f"Father: {father_name} ({father_gender}) - {father_id} [{father_handle}]"
                    )
            except Exception as e:
                logger.debug(f"Failed to fetch father {father_handle}: {e}")

        # Get mother
        mother_handle = family_data.get("mother_handle", "")
        if mother_handle:
            try:
                mother_data = await client.make_api_call(
                    ApiCalls.GET_PERSON, tree_id=tree_id, handle=mother_handle
                )
                if mother_data:
                    mother_name = _extract_person_name(mother_data)
                    mother_gender = _get_gender_letter(mother_data.get("gender", 2))
                    mother_id = mother_data.get("gramps_id", "")
                    family_members.append(
                        f"Mother: {mother_name} ({mother_gender}) - {mother_id} [{mother_handle}]"
                    )
            except Exception as e:
                logger.debug(f"Failed to fetch mother {mother_handle}: {e}")

        # First line with family ID and handle
        if family_members:
            result += f"{' | '.join(family_members)} - {gramps_id} - [{handle}]\n"
        else:
            result += f"{gramps_id} - [{handle}]\n"

        # Relationship type
        relationship_type = family_data.get("type", "")
        if relationship_type:
            result += f"Type: {relationship_type}\n"

        # Marriage and divorce events
        extended = family_data.get("extended", {})
        events = extended.get("events", [])
        event_ref_list = family_data.get("event_ref_list", [])

        for i, event_ref in enumerate(event_ref_list):
            if i < len(events):
                event = events[i]
                event_type = event.get("type", "")

                if event_type.lower() == "marriage":
                    marriage_date = format_date(event.get("date", {}))
                    marriage_place = await format_place(
                        client, tree_id, event.get("place", ""), inline=True
                    )
                    if marriage_date or marriage_place:
                        result += f"Married: {marriage_date}"
                        if marriage_place:
                            result += f" - {marriage_place}"
                        result += "\n"

                elif event_type.lower() == "divorce":
                    divorce_date = format_date(event.get("date", {}))
                    divorce_place = await format_place(
                        client, tree_id, event.get("place", ""), inline=True
                    )
                    if divorce_date or divorce_place:
                        result += f"Divorced: {divorce_date}"
                        if divorce_place:
                            result += f" - {divorce_place}"
                        result += "\n"

        # Children
        child_ref_list = family_data.get("child_ref_list", [])
        if child_ref_list:
            child_names = []
            for child_ref in child_ref_list:
                child_handle = child_ref.get("ref", "")
                if child_handle:
                    try:
                        child_data = await client.make_api_call(
                            ApiCalls.GET_PERSON, tree_id=tree_id, handle=child_handle
                        )
                        if child_data:
                            child_name = _extract_person_name(child_data)
                            child_gender = _get_gender_letter(
                                child_data.get("gender", 2)
                            )
                            child_id = child_data.get("gramps_id", "")
                            child_names.append(
                                f"{child_name} ({child_gender}) - {child_id} [{child_handle}]"
                            )
                    except Exception as e:
                        logger.debug(f"Failed to fetch child {child_handle}: {e}")

            if child_names:
                result += f"Children: {', '.join(child_names)}\n"

        # Citations (using extended map)
        citation_list = family_data.get("citation_list", [])
        if citation_list:
            ext_citations = extended.get("citations", [])
            cit_map = {}
            for c in ext_citations:
                h = c.get("handle", "")
                if h:
                    cit_map[h] = c.get("gramps_id", "")
            cit_strs = []
            for h in citation_list:
                cit_id = cit_map.get(h, "")
                if cit_id:
                    cit_strs.append(f"{cit_id} [{h}]")
                elif h:
                    cit_strs.append(f"[{h}]")
            if cit_strs:
                result += f"Citations: {', '.join(cit_strs)}\n"

        # Tags
        tag_list = family_data.get("tag_list", [])
        if tag_list:
            ext_tags = extended.get("tags", [])
            tag_map = {}
            for t in ext_tags:
                h = t.get("handle", "")
                if h:
                    tag_map[h] = t.get("name", "")
            tag_strs = []
            for h in tag_list:
                tag_name = tag_map.get(h, "")
                tag_str = (tag_name if tag_name else h) + f" [{h}]"
                tag_strs.append(tag_str)
            if tag_strs:
                result += f"Tags: {', '.join(tag_strs)}\n"

        # Attributes
        attribute_list = family_data.get("attribute_list", [])
        if attribute_list:
            attr_strs = [
                f"{a.get('type', '')}: {a.get('value', '')}"
                for a in attribute_list
                if a.get("type") or a.get("value")
            ]
            if attr_strs:
                result += f"Attributes: {'; '.join(attr_strs)}\n"

        # Events (all events with roles)
        event_list = []
        for i, event_ref in enumerate(event_ref_list):
            if i < len(events):
                event = events[i]
                event_type = event.get("type", "")
                event_gramps_id = event.get("gramps_id", "")
                event_handle_ev = event.get("handle", "")

                # Get role from event_ref
                role = event_ref.get("role", "") if isinstance(event_ref, dict) else ""
                if role:
                    entry = f"{event_type}, {role} ({event_gramps_id})"
                else:
                    entry = f"{event_type} ({event_gramps_id})"
                if event_handle_ev:
                    entry += f" [{event_handle_ev}]"
                event_list.append(entry)

        if event_list:
            result += f"Events: {', '.join(event_list)}\n"

        # Attached media
        media_list = family_data.get("media_list", [])
        if media_list:
            media_ids = []
            for media_ref in media_list:
                media_handle = (
                    media_ref.get("ref", "")
                    if isinstance(media_ref, dict)
                    else media_ref
                )
                if media_handle:
                    try:
                        media_data = await client.make_api_call(
                            api_call=ApiCalls.GET_MEDIA,
                            tree_id=tree_id,
                            handle=media_handle,
                        )
                        if media_data:
                            media_gramps_id = media_data.get("gramps_id", "")
                            if media_gramps_id:
                                media_ids.append(
                                    f"{media_gramps_id} [{media_handle}]"
                                )
                    except Exception:
                        continue

            if media_ids:
                result += f"Attached media: {', '.join(media_ids)}\n"

        # Attached notes
        note_list = family_data.get("note_list", [])
        if note_list:
            note_ids = []
            for note_handle in note_list:
                try:
                    note_data = await client.make_api_call(
                        api_call=ApiCalls.GET_NOTE, tree_id=tree_id, handle=note_handle
                    )
                    if note_data:
                        note_gramps_id = note_data.get("gramps_id", "")
                        if note_gramps_id:
                            note_ids.append(f"{note_gramps_id} [{note_handle}]")
                except Exception:
                    continue

            if note_ids:
                result += f"Attached notes: {', '.join(note_ids)}\n"

        # LDS Ordinations
        lds_ord_list = family_data.get("lds_ord_list", [])
        if lds_ord_list:
            lds_type_map = {
                "Baptism": "Baptism",
                "Endowment": "Endowment",
                "Sealed to Parents": "Sealed to Parents",
                "Sealed to Spouse": "Sealed to Spouse",
                "Confirmation": "Confirmation",
            }
            lds_strs = []
            for lds in lds_ord_list:
                lds_type = lds.get("type", "")
                lds_label = lds_type_map.get(lds_type, lds_type)
                lds_date = format_date(lds.get("date", {}))
                lds_temple = lds.get("temple", "")
                lds_status = lds.get("status", "")
                parts = [lds_label]
                if lds_date and lds_date != "date unknown":
                    parts.append(lds_date)
                if lds_temple:
                    parts.append(f"Temple: {lds_temple}")
                if lds_status:
                    parts.append(f"Status: {lds_status}")
                lds_strs.append(", ".join(parts))
            if lds_strs:
                result += "LDS Ordinations:\n"
                for s in lds_strs:
                    result += f"  {s}\n"

        # URLs
        urls = family_data.get("urls", [])
        if urls:
            for url in urls:
                if isinstance(url, dict):
                    url_path = url.get("path", "")
                    url_desc = url.get("description", "")
                    if url_path:
                        if url_desc:
                            result += f"{url_path} - {url_desc}\n"
                        else:
                            result += f"{url_path}\n"

        return result + "\n"

    except Exception as e:
        logger.debug(f"Failed to format family {handle}: {e}")
        return f"• **Family {handle}**\n  Error formatting family: {str(e)}\n\n"


def _extract_person_name(person_data: dict) -> str:
    """Extract full name from person data."""
    primary_name = person_data.get("primary_name", {})
    if primary_name:
        given_name = primary_name.get("first_name", "")
        surname_list = primary_name.get("surname_list", [])
        surname = surname_list[0].get("surname", "") if surname_list else ""
        full_name = f"{given_name} {surname}".strip()
        return full_name if full_name else ""
    return ""


def _get_gender_letter(gender: int) -> str:
    """Convert gender number to letter."""
    return {0: "F", 1: "M", 2: "U"}.get(gender, "U")
