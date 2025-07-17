from script import Recipe


class MealPlan:
    """
    MealPlan is a data class responsible for storing all the meals of a meal plan.
    """

    def __init__(self,
                 lunch: list[Recipe] | None = None,
                 breakfast: list[Recipe] | None = None,
                 snack: list[Recipe] | None = None,
                 misc: list[Recipe] | None = None):
        self.lunch: list[Recipe] = lunch or []
        self.breakfast: list[Recipe] = breakfast or []
        self.snack: list[Recipe] = snack or []
        self.misc: list[Recipe] = misc or []

    def as_list(self) -> list[Recipe]:
        return self.breakfast + self.lunch + self.snack
