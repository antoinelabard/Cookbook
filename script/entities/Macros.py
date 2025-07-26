class Macros:

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