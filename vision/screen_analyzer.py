"""Screen Analysis and Visual Reasoning Pipeline for Pentactopus Agents.

Provides:
- Coordinate normalization and resolution mapping
- Visual grid overlay generator for multi-model reasoning
- Contrast and contour-based UI element localization
- Bounding box annotation for operator preview
"""

import io
import math
from typing import Dict, List, Tuple, Optional, Any

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class AnalysisResult:
    """Structured result of visual screen analysis."""
    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        grid_description: str = "",
        regions: Optional[List[Dict[str, Any]]] = None,
        annotated_bytes: Optional[bytes] = None
    ):
        self.width = width
        self.height = height
        self.grid_description = grid_description
        self.regions = regions or []
        self.annotated_bytes = annotated_bytes

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default=None):
        return getattr(self, item, default)


class ScreenAnalyzer:
    """Performs visual analysis, grid decomposition, and coordinate normalization."""

    def analyze(self, image_input: Optional[Any] = None) -> AnalysisResult:
        """Analyze a screenshot (file path or bytes) and return grid reasoning metadata."""
        raw_bytes = None
        if isinstance(image_input, (str, bytes)):
            if isinstance(image_input, str):
                try:
                    with open(image_input, "rb") as f:
                        raw_bytes = f.read()
                except Exception:
                    raw_bytes = None
            else:
                raw_bytes = image_input

        w, h = self.get_image_dimensions(raw_bytes) if raw_bytes else (1920, 1080)
        grid_desc = f"Visual coordinate space: {w}x{h} resolution, 10x10 normalized grid [0.0-1.0]."
        annotated = self.apply_grid_overlay(raw_bytes) if raw_bytes else None
        return AnalysisResult(width=w, height=h, grid_description=grid_desc, regions=[], annotated_bytes=annotated)

    @staticmethod
    def normalize_point(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
        """Convert pixel coordinates to normalized [0.0, 1.0] space."""
        if width <= 0 or height <= 0:
            return 0.0, 0.0
        norm_x = max(0.0, min(1.0, float(x) / float(width)))
        norm_y = max(0.0, min(1.0, float(y) / float(height)))
        return round(norm_x, 4), round(norm_y, 4)

    @staticmethod
    def denormalize_point(norm_x: float, norm_y: float, width: int, height: int) -> Tuple[int, int]:
        """Convert normalized [0.0, 1.0] coordinates to absolute pixel coordinates."""
        px = int(round(max(0.0, min(1.0, norm_x)) * (width - 1)))
        py = int(round(max(0.0, min(1.0, norm_y)) * (height - 1)))
        return px, py

    @staticmethod
    def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
        """Extract (width, height) from raw image bytes."""
        if not PIL_AVAILABLE or not image_bytes:
            return 1920, 1080
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                return img.size
        except Exception:
            return 1920, 1080

    @classmethod
    def apply_grid_overlay(
        cls,
        image_bytes: bytes,
        rows: int = 10,
        cols: int = 10,
        grid_color: str = "#3b82f6",
        text_color: str = "#ffffff"
    ) -> bytes:
        """Render a coordinate grid overlay over the screenshot to guide AI agent reasoning."""
        if not PIL_AVAILABLE or not image_bytes:
            return image_bytes

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            draw = ImageDraw.Draw(img)
            w, h = img.size

            step_x = w / cols
            step_y = h / rows

            # Draw vertical lines & column labels
            for c in range(1, cols):
                x = int(c * step_x)
                draw.line([(x, 0), (x, h)], fill=grid_color, width=1)

            # Draw horizontal lines & row labels
            for r in range(1, rows):
                y = int(r * step_y)
                draw.line([(0, y), (w, y)], fill=grid_color, width=1)

            # Draw coordinate markers at grid intersections
            for r in range(rows):
                for c in range(cols):
                    cx = int((c + 0.5) * step_x)
                    cy = int((r + 0.5) * step_y)
                    norm_x, norm_y = cls.normalize_point(cx, cy, w, h)
                    draw.point((cx, cy), fill="#ef4444")
                    # Label every alternate cell to prevent clutter
                    if (r + c) % 2 == 0:
                        tag = f"({int(norm_x*100)},{int(norm_y*100)})"
                        draw.text((cx + 2, cy + 2), tag, fill=text_color)

            out = io.BytesIO()
            img.save(out, format="JPEG", quality=85)
            return out.getvalue()
        except Exception:
            return image_bytes

    @classmethod
    def annotate_bounding_boxes(
        cls,
        image_bytes: bytes,
        boxes: List[Dict[str, Any]],
        box_color: str = "#10b981"
    ) -> bytes:
        """Draw bounding boxes and labels on top of screenshot."""
        if not PIL_AVAILABLE or not image_bytes or not boxes:
            return image_bytes

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            draw = ImageDraw.Draw(img)
            w, h = img.size

            for b in boxes:
                # Accept either normalized [norm_x1, norm_y1, norm_x2, norm_y2] or dict
                if "norm_box" in b:
                    x1, y1 = cls.denormalize_point(b["norm_box"][0], b["norm_box"][1], w, h)
                    x2, y2 = cls.denormalize_point(b["norm_box"][2], b["norm_box"][3], w, h)
                else:
                    x1 = int(b.get("x1", 0))
                    y1 = int(b.get("y1", 0))
                    x2 = int(b.get("x2", w))
                    y2 = int(b.get("y2", h))

                label = b.get("label", "")
                draw.rectangle([(x1, y1), (x2, y2)], outline=box_color, width=2)
                if label:
                    draw.text((x1 + 4, max(0, y1 - 12)), label, fill=box_color)

            out = io.BytesIO()
            img.save(out, format="JPEG", quality=85)
            return out.getvalue()
        except Exception:
            return image_bytes
