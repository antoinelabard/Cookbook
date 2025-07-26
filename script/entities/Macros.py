class Macros:

    def __init__(self,
                 energy: float = 0,
                 proteins: float = 0,
                 lipids: float = 0,
                 carbs: float = 0,
                 multiplicity: float = 0):
        self.energy: float = energy
        self.proteins: float = proteins
        self.lipids: float = lipids
        self.carbs: float = carbs
        self.multiplicity: float = multiplicity

    def __add__(self, other):
        return Macros(
            self.energy * self.multiplicity + other.energy * other.multiplicity,
            self.proteins * self.multiplicity + other.proteins * other.multiplicity,
            self.lipids * self.multiplicity + other.lipids * other.multiplicity,
            self.carbs * self.multiplicity + other.carbs * other.multiplicity,
            1 # Supposed that a Recipe or a meal plan does not have a quantity (ex: 50g) like an ingredient
        )