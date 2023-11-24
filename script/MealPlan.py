from script import Recipe


class MealPlans:
    def __init__(self,
                 lunches: list[Recipe],
                 breakfasts: list[Recipe],
                 snacks: list[Recipe]):
        self.lunches: list[Recipe] = lunches
        self.breakfasts: list[Recipe] = breakfasts
        self.snacks: list[Recipe] = snacks
