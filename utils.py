from pathlib import Path
import os
import sys

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_art_path(filename: str) -> str:
    """
    Retorna o caminho absoluto de um arquivo dentro da pasta Arte.
    """
    return resource_path(os.path.join("Arte", filename))