from typing import Self


class Macros:
    MACROS = "macros"
    ENERGY = "energy"
    PROTEINS = "proteins"
    FAT = "fat"
    CARBS = "carbs"
    PORTIONS = "portions"
    PIECE_TO_G_RATIO = "piece_to_g_ratio"
    REFERENCE_QUANTITY = 100  # in g, a macros indicates the nutrients for 100g

    def __init__(self,
                 energy: float = 0,
                 proteins: float = 0,
                 fat: float = 0,
                 carbs: float = 0):
        self._energy: float = energy
        self._proteins: float = proteins
        self._fat: float = fat
        self._carbs: float = carbs

    def get_energy(self) -> float:
        return self._energy

    def get_proteins(self) -> float:
        return self._proteins

    def get_fat(self) -> float:
        return self._fat

    def get_carbs(self) -> float:
        return self._carbs

    def __add__(self, other: Self) -> Self:
        return Macros(
            self._energy + other.get_energy(),
            self._proteins + other.get_proteins(),
            self._fat + other.get_fat(),
            self._carbs + other.get_carbs(),
        )

    def __mul__(self, other: float) -> Self:
        return Macros(
            self._energy * other,
            self._proteins * other,
            self._fat * other,
            self._carbs * other,
        )

    def __truediv__(self, other: float) -> Self:
        return Macros(
            self._energy / other,
            self._proteins / other,
            self._fat / other,
            self._carbs / other,
        )

    def to_markdown_table(self):
        return (
                "| Énergie | Protéines | Lipides | Glucides |\n"
                + "|:-------:|:---------:|:-------:|:--------:|\n"
                + f"| {round(self._energy)} | {round(self._proteins)} | {round(self._fat)} | {round(self._carbs)} |")
