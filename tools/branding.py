"""Override the Arabic settings credit without modifying the original mod."""
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
    return {MENU_PATH: updated.encode("utf-8")}
