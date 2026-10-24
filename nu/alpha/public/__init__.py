"""Public API of the alpha module.

Alphabet of the ScrubLar domain: PII types, errors, and (inherited
from BaseLar) the IEvent marker.
"""

from nu.alpha.public.events import IEvent as IEvent
from nu.alpha.public.types import (
    DetectionConfig as DetectionConfig,
)
from nu.alpha.public.types import (
    DetectionError as DetectionError,
)
from nu.alpha.public.types import (
    DetectionReport as DetectionReport,
)
from nu.alpha.public.types import (
    MaskingError as MaskingError,
)
from nu.alpha.public.types import (
    MaskResult as MaskResult,
)
from nu.alpha.public.types import (
    ParsingError as ParsingError,
)
from nu.alpha.public.types import (
    PIIEntity as PIIEntity,
)
from nu.alpha.public.types import (
    PIIKind as PIIKind,
)
from nu.alpha.public.types import (
    ScrubLarError as ScrubLarError,
)
from nu.alpha.public.types import (
    UnsupportedFormatError as UnsupportedFormatError,
)

__all__ = [
    "DetectionConfig",
    "DetectionError",
    "DetectionReport",
    "IEvent",
    "MaskResult",
    "MaskingError",
    "ParsingError",
    "PIIEntity",
    "PIIKind",
    "ScrubLarError",
    "UnsupportedFormatError",
]
