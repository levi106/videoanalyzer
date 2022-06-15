from typing import Any, Dict, Tuple

class BaseSink:
    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        pass

    def reset(self) -> None:
        pass