"""Package configuration."""

from pathlib import Path
import typing as t

CLASS_NAME_DICT_CONSTRUCTIBLE: t.Final[str] = "DictConstructible"
CLASS_NAME_DATA_CLASS: t.Final[str] = "DataClass"
CLASS_NAME_POD_WRAPPER: t.Final[str] = "PodWrapper"
METHOD_NAME_FROM_DICT_WITH_CAST: t.Final[str] = "from_dict_with_cast"
PACKAGE_ROOT: t.Final[Path] = Path(__file__).parent
TEMPLATE_PATH: t.Final[Path] = PACKAGE_ROOT / "template.py"
TEMPLATE_LOC_GENERATED_CLASSES: t.Final[str] = "SANDALS::GENERATED_CLASSES"
ROW_ID_COL_NAME: t.Final[str] = "row_id"
