from ._baseprocessor import BaseProcessor
from typing import Any, Dict, Optional, Tuple


class NullProcessor(BaseProcessor):
    def process(self, frame: Any, props: Dict[str, Any]) -> Optional[Tuple[Any, Dict[str, Any]]]:
        return frame, props
