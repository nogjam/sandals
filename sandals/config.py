"""Package configuration."""

from pathlib import Path


PACKAGE_ROOT: Path = Path(__file__).parent
TEMPLATE_PATH: Path = PACKAGE_ROOT / "template.py"
TEMPLATE_LOC_GENERATED_CLASSES = "SANDALS::GENERATED_CLASSES"
ROW_ID_COL_NAME = "row_id"
