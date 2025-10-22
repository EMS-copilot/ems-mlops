from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class BatchInfo:
    index: List[str]
