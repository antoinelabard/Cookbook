class Macros:

    REFERENCE_QUANTITY = 100 # in g, a macros indicates the nutrients for 100g

    def __init__(self,
                 energy: float = 0,
                 proteins: float = 0,
                 lipids: float = 0,
                 carbs: float = 0):
        self.energy: float = energy
        self.proteins: float = proteins
        self.lipids: float = lipids
        self.carbs: float = carbs

    def __add__(self, other):
        return Macros(
            self.energy + other.energy,
            self.proteins + other.proteins,
            self.lipids + other.lipids,
            self.carbs + other.carbs,
        )

    def __mul__(self, other):
        return Macros(
            self.energy * other,
            self.proteins * other,
            self.lipids * other,
            self.carbs * other,
        )

    def __truediv__(self, other):
        return Macros(
            self.energy / other,
            self.proteins / other,
            self.lipids / other,
            self.carbs / other,
            )

    def to_markdown_table(self):
        return (
                "| Énergie | Protéines | Lipides | Glucides |\n"
                + "|:-------:|:---------:|:-------:|:--------:|\n"
                + f"| {self.energy} | {self.proteins} | {self.lipids} | {self.carbs} |")