"""Package configuration."""

from pathlib import Path
import typing as t


PACKAGE_ROOT: t.Final[Path] = Path(__file__).parent
TEMPLATE_PATH: t.Final[Path] = PACKAGE_ROOT / "template.py"
TEMPLATE_LOC_GENERATED_CLASSES: t.Final[str] = "SANDALS::GENERATED_CLASSES"
ROW_ID_COL_NAME: t.Final[str] = "row_id"
