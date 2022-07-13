from typing import Any, Dict, Tuple


class BaseSource:
    def read(self):
        pass

    def reset(self) -> None:
        pass
