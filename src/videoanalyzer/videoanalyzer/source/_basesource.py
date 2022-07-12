from typing import Any, Dict, Tuple


class BaseSource:
    def read(self) -> Tuple[Any, Dict[str, Any]]:
        pass

    def reset(self) -> None:
        pass
