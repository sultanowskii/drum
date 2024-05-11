from dataclasses import dataclass


@dataclass
class Iota:
    """
    Simplifies definition of incrementing numbers.

    Usage example:

    ```python
    iota = Iota(3)

    a = iota() # 3
    b = iota() # 4
    c = iota() # 5
    ```
    """
    cntr: int = 0

    def __call__(self) -> int:
        current = self.cntr
        self.cntr += 1
        return current
