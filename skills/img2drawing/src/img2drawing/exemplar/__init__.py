"""R23 compatibility implementation for historical grammar-exemplar tooling.

The deployable vNext skill intentionally has no canonical exemplar workflow or examples
tree. New drawing work must not depend on this package; it remains importable only for
explicit R23 compatibility until the bounded retirement decision.
"""

from .ablation import *
