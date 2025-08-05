from typing import Self


class Macros:
    REFERENCE_QUANTITY = 100  # in g, a macros indicates the nutrients for 100g

    def __init__(self,
                 energy: float = 0,
                 proteins: float = 0,
                 lipids: float = 0,
                 carbs: float = 0):
        self._energy: float = energy
        self._proteins: float = proteins
        self._lipids: float = lipids
        self._carbs: float = carbs

    def get_energy(self) -> float:
        return self._energy

    def get_proteins(self) -> float:
        return self._proteins

    def get_lipids(self) -> float:
        return self._lipids

    def get_carbs(self) -> float:
        return self._carbs

    def __add__(self, other: Self) -> Self:
        return Macros(
            self._energy + other.get_energy(),
            self._proteins + other.get_proteins(),
            self._lipids + other.get_lipids(),
            self._carbs + other.get_carbs(),
        )

    def __mul__(self, other: float) -> Self:
        return Macros(
            self._energy * other,
            self._proteins * other,
            self._lipids * other,
            self._carbs * other,
        )

    def __truediv__(self, other: float) -> Self:
        return Macros(
            self._energy / other,
            self._proteins / other,
            self._lipids / other,
            self._carbs / other,
        )

    def to_markdown_table(self):
        return (
                "| Énergie | Protéines | Lipides | Glucides |\n"
                + "|:-------:|:---------:|:-------:|:--------:|\n"
                + f"| {self._energy} | {self._proteins} | {self._lipids} | {self._carbs} |")
