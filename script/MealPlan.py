from script import Recipe


class MealPlan:
    def __init__(self,
                 lunch=None,
                 breakfast=None,
                 snack=None):
        self.lunch: list[Recipe] = lunch or []
        self.breakfast: list[Recipe] = breakfast or []
        self.snack: list[Recipe] = snack or []
