from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_CANONICAL_BOOTSTRAP = Path(__file__).resolve().parents[1] / "_bootstrap.py"
_SPEC = spec_from_file_location("prompt_vault_scripts_bootstrap", _CANONICAL_BOOTSTRAP)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Unable to load canonical bootstrap: {_CANONICAL_BOOTSTRAP}")
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
ROOT = _MODULE.ROOT
