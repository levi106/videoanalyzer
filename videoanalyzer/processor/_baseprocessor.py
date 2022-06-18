from typing import Any, Dict, Tuple, Optional

class BaseProcessor:
    def process(self, frame: Any, props: Dict[str, Any]) -> Optional[Tuple[Any,Dict[str,Any]]]:
        pass

    def reset(self) -> None:
        pass
