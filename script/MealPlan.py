from script import Recipe


class MealPlan:
    def __init__(self,
                 lunches=None,
                 breakfasts=None,
                 snacks=None):
        self.lunches: list[Recipe] = lunches or []
        self.breakfasts: list[Recipe] = breakfasts or []
        self.snacks: list[Recipe] = snacks or []
