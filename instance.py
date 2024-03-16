from dataclasses import dataclass
from class_definitions import Class
from typing import Dict, Any


@dataclass
class Instance:
    class_type: Class
    name: str
    attributes: Dict[str, Any]
