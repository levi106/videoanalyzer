from typing import Any, Dict, Tuple, Optional
from ..processor import BaseProcessor

class BaseSink(BaseProcessor):
    def process(self, frame: Any, props: Dict[str,Any]) -> Optional[Tuple[Any,Dict[str,Any]]]:
        self.write(frame, props)
        return None

    def write(self, frame: Any, props: Dict[str,Any]) -> None:
        pass

    def reset(self) -> None:
        pass