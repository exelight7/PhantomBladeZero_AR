"""استبدال اسم التعريب في ملف القائمة الرئيسية دون المساس بالحزمة المرجعية."""
from pak import read_pak
from pbzlib import SRC_PAK

MENU_PATH = "ProjectPBZ/Content/JavaScript/UI/Widget/StartMenu.js"
DISPLAY_NAME = "exelight7"


def menu_override():
    source = read_pak(SRC_PAK)[MENU_PATH].decode("utf-8")
    old = ' + " - تعريب عباديوه"'
    if source.count(old) != 1:
        raise ValueError("Original settings credit changed; review StartMenu.js before rebuilding")
    updated = source.replace(old, f' + " - تعريب {DISPLAY_NAME}"')
    updated = updated.replace("// تعريب عباديوه:", f"// تعريب {DISPLAY_NAME}:")
    if "عباديوه" in updated or "3badioh" in updated.lower():
        raise ValueError("Upstream name still appears in StartMenu.js; review before rebuilding")
    return {MENU_PATH: updated.encode("utf-8")}
