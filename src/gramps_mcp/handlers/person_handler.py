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
Person detail handler for Gramps MCP operations.
"""

from ..models.api_calls import ApiCalls
from .date_handler import format_date
from .place_handler import format_place


async def format_person(client, tree_id: str, handle: str) -> str:
    """Format comprehensive person data with timeline and citations."""
    # Get person data
    person_data = await client.make_api_call(
        ApiCalls.GET_PERSON, tree_id=tree_id, handle=handle, params={"extend": "all"}
    )

    # Get person timeline
    timeline_data = await client.make_api_call(
        ApiCalls.GET_PERSON_TIMELINE,
        tree_id=tree_id,
        handle=handle,
        params={"ratings": True},  # Include citation confidence
    )

    result = "=== PERSON DETAILS ===\n"

    # Extract basic info
    gramps_id = person_data.get("gramps_id", "")
    name = _extract_person_name(person_data)
    gender_display = _get_gender_letter(person_data.get("gender", 2))

    result += f"{name} ({gender_display}) - {gramps_id} - [{handle}]\n"

    # Alternate names (married names, maiden names, etc.)
    alternate_names = person_data.get("alternate_names", [])
    if alternate_names:
        alt_name_strs = []
        for alt_name in alternate_names:
            alt_given = alt_name.get("first_name", "")
            alt_surname_list = alt_name.get("surname_list", [])
            alt_surname = alt_surname_list[0].get("surname", "") if alt_surname_list else ""
            alt_full = f"{alt_given} {alt_surname}".strip()
            alt_type = alt_name.get("type", "")
            if isinstance(alt_type, dict):
                alt_type = alt_type.get("string", "") or alt_type.get("_class", "")
            if alt_full:
                if alt_type:
                    alt_name_strs.append(f"{alt_full} ({alt_type})")
                else:
                    alt_name_strs.append(alt_full)
        if alt_name_strs:
            result += f"Also known as: {', '.join(alt_name_strs)}\n"

    # Birth and death from extended data
    extended = person_data.get("extended", {})
    events = extended.get("events", [])

    # Birth event
    birth_ref_index = person_data.get("birth_ref_index", -1)
    if birth_ref_index >= 0 and birth_ref_index < len(events):
        birth_event = events[birth_ref_index]
        birth_date = format_date(birth_event.get("date", {}))
        birth_place = await format_place(
            client, tree_id, birth_event.get("place", ""), inline=True
        )
        result += f"Born: {birth_date} - {birth_place}\n"

    # Death event
    death_ref_index = person_data.get("death_ref_index", -1)
    if death_ref_index >= 0 and death_ref_index < len(events):
        death_event = events[death_ref_index]
        death_date = format_date(death_event.get("date", {}))
        death_place = await format_place(
            client, tree_id, death_event.get("place", ""), inline=True
        )
        result += f"Died: {death_date} - {death_place}\n"

    # Relations section
    result += "\Relations:\n"

    # Parents section
    result += "Parents:\n"
    parent_family_list = person_data.get("parent_family_list", [])

    for family_handle in parent_family_list:
        try:
            family_data = await client.make_api_call(
                ApiCalls.GET_FAMILY,
                tree_id=tree_id,
                handle=family_handle,
                params={"extend": "all"},
            )
            extended = family_data.get("extended", {})

            # Father
            father = extended.get("father", {})
            if father:
                father_name = _extract_person_name(father)
                father_id = father.get("gramps_id", "")
                father_handle = father.get("handle", "")
                father_birth, father_death = await _get_birth_death_dates(
                    client, tree_id, father
                )
                dates = ", ".join(filter(None, [father_birth, father_death]))
                line = f"- {father_name} - {father_id}"
                if father_handle:
                    line += f" [{father_handle}]"
                if dates:
                    line += f" - {dates}"
                result += line + "\n"

            # Mother
            mother = extended.get("mother", {})
            if mother:
                mother_name = _extract_person_name(mother)
                mother_id = mother.get("gramps_id", "")
                mother_handle = mother.get("handle", "")
                mother_birth, mother_death = await _get_birth_death_dates(
                    client, tree_id, mother
                )
                dates = ", ".join(filter(None, [mother_birth, mother_death]))
                line = f"- {mother_name} - {mother_id}"
                if mother_handle:
                    line += f" [{mother_handle}]"
                if dates:
                    line += f" - {dates}"
                result += line + "\n"

            # Siblings (other children in same family)
            children = extended.get("children", [])
            siblings = [
                child for child in children if child.get("gramps_id", "") != gramps_id
            ]
            if siblings:
                result += "Siblings:\n"
                for sibling in siblings:
                    sibling_name = _extract_person_name(sibling)
                    sibling_id = sibling.get("gramps_id", "")
                    sibling_handle = sibling.get("handle", "")
                    sibling_birth, sibling_death = await _get_birth_death_dates(
                        client, tree_id, sibling
                    )
                    dates = ", ".join(filter(None, [sibling_birth, sibling_death]))
                    line = f"- {sibling_name} - {sibling_id}"
                    if sibling_handle:
                        line += f" [{sibling_handle}]"
                    if dates:
                        line += f" - {dates}"
                    result += line + "\n"

        except Exception:
            continue

    # Spouses and children
    family_list = person_data.get("family_list", [])
    for family_handle in family_list:
        try:
            family_data = await client.make_api_call(
                ApiCalls.GET_FAMILY,
                tree_id=tree_id,
                handle=family_handle,
                params={"extend": "all"},
            )
            extended = family_data.get("extended", {})

            # Determine spouse (father or mother that's not this person)
            father = extended.get("father", {})
            mother = extended.get("mother", {})

            spouse = None
            if father and father.get("gramps_id", "") != gramps_id:
                spouse = father
            elif mother and mother.get("gramps_id", "") != gramps_id:
                spouse = mother

            if spouse:
                spouse_name = _extract_person_name(spouse)
                spouse_id = spouse.get("gramps_id", "")
                spouse_handle = spouse.get("handle", "")
                spouse_birth, spouse_death = await _get_birth_death_dates(
                    client, tree_id, spouse
                )
                dates = ", ".join(filter(None, [spouse_birth, spouse_death]))
                line = f"- {spouse_name} - {spouse_id}"
                if spouse_handle:
                    line += f" [{spouse_handle}]"
                if dates:
                    line += f" - {dates}"
                result += f"Spouse:\n{line}\n"

                # Children of this spouse
                children = extended.get("children", [])
                if children:
                    result += "Children:\n"
                    for child in children:
                        child_name = _extract_person_name(child)
                        child_id = child.get("gramps_id", "")
                        child_handle = child.get("handle", "")
                        child_birth, child_death = await _get_birth_death_dates(
                            client, tree_id, child
                        )
                        dates = ", ".join(filter(None, [child_birth, child_death]))
                        line = f"- {child_name} - {child_id}"
                        if child_handle:
                            line += f" [{child_handle}]"
                        if dates:
                            line += f" - {dates}"
                        result += line + "\n"
        except Exception:
            continue

    # Timeline section
    result += "\Timeline:\n"
    if timeline_data:
        for timeline_event in timeline_data:
            if not isinstance(timeline_event, dict):
                continue

            # Basic event info from timeline
            event_type = timeline_event.get("type", "Unknown")
            event_id = timeline_event.get("gramps_id", "")
            role = timeline_event.get("role", "Primary")
            event_handle = timeline_event.get("handle", "")

            # Get properly formatted date using format_date function
            event_date = "date unknown"
            event_data = None
            if event_handle:
                try:
                    event_data = await client.make_api_call(
                        ApiCalls.GET_EVENT, tree_id=tree_id, handle=event_handle
                    )
                    event_date = format_date(event_data.get("date", {}))
                except Exception:
                    # Fallback to timeline date if event fetch fails
                    event_date = timeline_event.get("date", "date unknown")

            # Place - use display_name directly from timeline data
            place_data = timeline_event.get("place", {})
            place_name = (
                place_data.get("display_name", "")
                if isinstance(place_data, dict)
                else ""
            )
            place_part = f"({place_name})" if place_name else "()"

            # Participant info - extract from person data in timeline
            participant_name = ""
            participant_id = ""
            person_data_in_timeline = timeline_event.get("person", {})

            if person_data_in_timeline:
                relationship = person_data_in_timeline.get("relationship", "")
                if relationship == "self":
                    # This person's event
                    participant_name = _extract_person_name(person_data)
                    participant_id = person_data.get("gramps_id", "")
                else:
                    # Other person's event - use data from timeline
                    given_name = person_data_in_timeline.get("name_given", "")
                    surname = person_data_in_timeline.get("name_surname", "")
                    participant_name = f"{given_name} {surname}".strip()
                    participant_id = person_data_in_timeline.get("gramps_id", "")

            # Format the timeline entry
            participant_part = (
                f", {participant_name} {participant_id}, {role}"
                if participant_name
                else f", {role}"
            )
            result += (
                f"- {event_date} {place_part} - {event_id} : "
                f"{event_type}{participant_part}\n"
            )

            # Add citations if we have event data - reuse the event_data from above
            if event_data:
                try:
                    citation_list = event_data.get("citation_list", [])
                    citation_ids = []
                    for citation_handle in citation_list:
                        citation_data = await client.make_api_call(
                            ApiCalls.GET_CITATION,
                            tree_id=tree_id,
                            handle=citation_handle,
                        )
                        citation_id = citation_data.get("gramps_id", "")
                        if citation_id:
                            citation_ids.append(citation_id)

                    if citation_ids:
                        result += f"  Citations: {', '.join(citation_ids)}\n"
                except Exception:
                    pass

    # Re-read extended after timeline loop (may have been shadowed by inner scopes)
    extended = person_data.get("extended", {})

    # Tags
    tag_list = person_data.get("tag_list", [])
    if tag_list:
        extended_tags = extended.get("tags", [])
        tag_map = {t.get("handle"): t for t in extended_tags}
        tag_strs = []
        for h in tag_list:
            if h in tag_map:
                tag_name = tag_map[h].get("name", "")
                tag_strs.append(f"{tag_name} [{h}]" if tag_name else f"[{h}]")
        if tag_strs:
            result += f"\nTags: {', '.join(tag_strs)}\n"

    # Attributes
    attribute_list = person_data.get("attribute_list", [])
    if attribute_list:
        attr_strs = []
        for attr in attribute_list:
            attr_type = attr.get("type", "")
            if isinstance(attr_type, dict):
                attr_type = attr_type.get("string", "") or attr_type.get("_class", "")
            attr_value = attr.get("value", "")
            if attr_type and attr_value:
                attr_strs.append(f"{attr_type}: {attr_value}")
        if attr_strs:
            result += f"\nAttributes: {'; '.join(attr_strs)}\n"

    # Associations (godparent, friend, etc.)
    person_ref_list = person_data.get("person_ref_list", [])
    if person_ref_list:
        extended_people = extended.get("people", [])
        person_map = {}
        for p in extended_people:
            p_handle = p.get("handle", "")
            pn = p.get("primary_name", {})
            given = pn.get("first_name", "")
            surnames = pn.get("surname_list", [])
            surname = surnames[0].get("surname", "") if surnames else ""
            person_map[p_handle] = {
                "name": f"{given} {surname}".strip(),
                "gramps_id": p.get("gramps_id", ""),
            }
        assoc_strs = []
        for ref in person_ref_list:
            ref_handle = ref.get("ref", "")
            rel = ref.get("rel", "")
            info = person_map.get(ref_handle, {})
            ref_name = info.get("name", "")
            ref_id = info.get("gramps_id", "")
            if ref_name and rel:
                assoc_strs.append(f"{ref_name} ({rel}) - {ref_id} [{ref_handle}]")
            elif ref_name:
                assoc_strs.append(f"{ref_name} - {ref_id} [{ref_handle}]")
            else:
                assoc_strs.append(f"{ref_id} [{ref_handle}]" if ref_id else f"[{ref_handle}]")
        if assoc_strs:
            result += f"\nAssociations: {', '.join(assoc_strs)}\n"

    # Addresses
    address_list = person_data.get("address_list", [])
    if address_list:
        result += "\nAddresses:\n"
        for addr in address_list:
            addr_date = format_date(addr.get("date", {}))
            parts = [
                addr.get("street", ""),
                addr.get("locality", ""),
                addr.get("city", ""),
                addr.get("county", ""),
                addr.get("state", ""),
                addr.get("postal", ""),
                addr.get("country", ""),
            ]
            addr_str = ", ".join(p for p in parts if p)
            phone = addr.get("phone", "")
            line = f"  {addr_str}"
            if phone:
                line += f" | {phone}"
            if addr_date:
                line += f" ({addr_date})"
            result += line + "\n"

    # Direct citations on the person record
    citation_list = person_data.get("citation_list", [])
    if citation_list:
        extended_citations = extended.get("citations", [])
        cit_map = {c.get("handle"): c for c in extended_citations}
        cit_strs = []
        for h in citation_list:
            if h in cit_map:
                cit_id = cit_map[h].get("gramps_id", h)
                cit_strs.append(f"{cit_id} [{h}]")
        if cit_strs:
            result += f"\nCitations: {', '.join(cit_strs)}\n"

    # LDS Ordinations
    lds_ord_list = person_data.get("lds_ord_list", [])
    if lds_ord_list:
        lds_type_map = {
            0: "Baptism", 1: "Endowment", 2: "Seal to Parents",
            3: "Seal to Spouse", 4: "Confirmation",
        }
        lds_status_map = {
            0: "None", 1: "BIC", 2: "Cancelled", 3: "Child",
            4: "Cleared", 5: "Completed", 6: "DNS", 7: "Infant",
            8: "Pre-1970", 9: "Qualified", 10: "DNS/CAN",
            11: "Stillborn", 12: "Submitted", 13: "Uncleared",
        }
        result += "\nLDS Ordinations:\n"
        for lds in lds_ord_list:
            lds_type = lds_type_map.get(lds.get("type"), str(lds.get("type", "")))
            lds_date = format_date(lds.get("date", {}))
            temple = lds.get("temple", "")
            status = lds_status_map.get(lds.get("status"), "")
            line = f"  {lds_type}"
            if lds_date:
                line += f" - {lds_date}"
            if temple:
                line += f" @ {temple}"
            if status:
                line += f" [{status}]"
            result += line + "\n"

    # URLs
    urls = person_data.get("urls", [])
    if urls:
        result += "\nURLs:\n"
        for url in urls:
            if isinstance(url, dict):
                url_path = url.get("path", "")
                url_desc = url.get("description", "")
                if url_path:
                    result += f"{url_path}{' - ' + url_desc if url_desc else ''}\n"

    # Attached media section
    result += "\nAttached media:\n"
    media_list = person_data.get("media_list", [])
    for media_ref in media_list:
        media_handle = media_ref.get("ref", "")
        if media_handle:
            media_data = await client.make_api_call(
                ApiCalls.GET_MEDIA_ITEM, tree_id=tree_id, handle=media_handle
            )
            media_desc = media_data.get("desc", "")
            media_id = media_data.get("gramps_id", "")
            result += f"- {media_desc} ({media_id})\n"

    # Attached notes section
    result += "\nAttached notes:\n"
    note_list = person_data.get("note_list", [])
    for note_handle in note_list:
        note_data = await client.make_api_call(
            ApiCalls.GET_NOTE, tree_id=tree_id, handle=note_handle
        )
        note_type = note_data.get("type", "")
        note_id = note_data.get("gramps_id", "")
        # Extract string value from text field (may be dict or string)
        text_value = note_data.get("text", "")
        if isinstance(text_value, dict) and "string" in text_value:
            text_value = text_value["string"]
        text_str = str(text_value) if text_value else ""
        note_text = text_str[:50]
        if len(text_str) > 50:
            note_text += "..."
        result += f"- {note_type}: {note_text} ({note_id})\n"

    return result


def _extract_person_name(person_data: dict) -> str:
    """Extract full name from person data."""
    primary_name = person_data.get("primary_name", {})
    if primary_name:
        given_name = primary_name.get("first_name", "")
        surname_list = primary_name.get("surname_list", [])
        surname = surname_list[0].get("surname", "") if surname_list else ""
        return f"{given_name} {surname}".strip()
    return "Unknown"


def _get_gender_letter(gender: int) -> str:
    """Convert gender number to letter."""
    return {0: "F", 1: "M", 2: "U"}.get(gender, "U")


async def _get_birth_death_dates(client, tree_id: str, person_data: dict) -> tuple:
    """Get birth and death dates for a person."""
    person_handle = person_data.get("handle", "")
    if not person_handle:
        return "", ""

    try:
        # Get person with extended data to access events
        full_person_data = await client.make_api_call(
            ApiCalls.GET_PERSON,
            tree_id=tree_id,
            handle=person_handle,
            params={"extend": "all"},
        )

        extended = full_person_data.get("extended", {})
        events = extended.get("events", [])

        birth_date = ""
        death_date = ""

        # Check for birth event
        birth_ref_index = full_person_data.get("birth_ref_index", -1)
        if birth_ref_index >= 0 and birth_ref_index < len(events):
            birth_event = events[birth_ref_index]
            birth_date = format_date(birth_event.get("date", {}))

        # Check for death event
        death_ref_index = full_person_data.get("death_ref_index", -1)
        if death_ref_index >= 0 and death_ref_index < len(events):
            death_event = events[death_ref_index]
            death_date = format_date(death_event.get("date", {}))

        # If still living, show as such
        if full_person_data.get("living", False):
            death_date = "Living"

        return birth_date, death_date

    except Exception:
        return "", ""
