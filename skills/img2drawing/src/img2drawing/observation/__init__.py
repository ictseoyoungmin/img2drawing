"""Current observation-side material sampling helpers.

Historical R23 observation contracts, lock records, uncertainty records, and view helpers were
retired with the R23 orchestration runtime. Subject/material palette sampling remains a documented
specialized capability and is intentionally independent of drawing-session orchestration.
"""

from .palette import MaterialSample, SubjectPalette

__all__ = ["MaterialSample", "SubjectPalette"]
