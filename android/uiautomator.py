"""Android UI Hierarchy parser and accessibility inspector."""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

@dataclass
class UIElement:
    node_id: int
    text: str
    content_desc: str
    resource_id: str
    class_name: str
    package: str
    bounds: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: Tuple[int, int]            # (cx, cy)
    is_clickable: bool
    is_scrollable: bool

class UIHierarchyParser:
    """Parses Android uiautomator XML dump into structured interactive elements."""

    BOUNDS_PATTERN = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")

    @classmethod
    def parse(cls, xml_content: str) -> List[UIElement]:
        if not xml_content or "<hierarchy" not in xml_content:
            return []

        clean_xml = xml_content[xml_content.find("<hierarchy"):]
        try:
            root = ET.fromstring(clean_xml)
        except ET.ParseError:
            return []

        elements = []
        node_counter = 0

        for node in root.iter("node"):
            bounds_str = node.attrib.get("bounds", "")
            match = cls.BOUNDS_PATTERN.match(bounds_str)
            if not match:
                continue

            x1, y1, x2, y2 = map(int, match.groups())
            # Skip invisible / zero-size nodes
            if x2 <= x1 or y2 <= y1:
                continue

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            text = node.attrib.get("text", "").strip()
            desc = node.attrib.get("content-desc", "").strip()
            res_id = node.attrib.get("resource-id", "").strip()
            cls_name = node.attrib.get("class", "").strip()
            pkg = node.attrib.get("package", "").strip()
            clickable = node.attrib.get("clickable", "false").lower() == "true"
            scrollable = node.attrib.get("scrollable", "false").lower() == "true"

            # Filter for elements that contain meaningful semantics or interaction
            if text or desc or res_id or clickable:
                node_counter += 1
                elements.append(UIElement(
                    node_id=node_counter,
                    text=text,
                    content_desc=desc,
                    resource_id=res_id,
                    class_name=cls_name,
                    package=pkg,
                    bounds=(x1, y1, x2, y2),
                    center=(cx, cy),
                    is_clickable=clickable,
                    is_scrollable=scrollable
                ))

        return elements

    @classmethod
    def to_readable_state(cls, elements: List[UIElement]) -> str:
        """Format elements into a concise text representation for LLM prompt."""
        lines = []
        for el in elements:
            label = el.text or el.content_desc or el.resource_id.split("/")[-1] or "Element"
            flags = []
            if el.is_clickable:
                flags.append("clickable")
            if el.is_scrollable:
                flags.append("scrollable")
            flag_str = f"[{', '.join(flags)}]" if flags else ""
            lines.append(f"ID={el.node_id} | '{label}' | Center=({el.center[0]},{el.center[1]}) {flag_str}")
        return "\n".join(lines)

    @classmethod
    def find_by_text(cls, elements: List[UIElement], query: str, case_sensitive: bool = False) -> List[UIElement]:
        query_norm = query if case_sensitive else query.lower()
        results = []
        for el in elements:
            t = el.text if case_sensitive else el.text.lower()
            d = el.content_desc if case_sensitive else el.content_desc.lower()
            if query_norm in t or query_norm in d:
                results.append(el)
        return results
