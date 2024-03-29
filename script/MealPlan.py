from script import Recipe


class MealPlan:
    """
    MealPlan is a data class responsible for storing all the meals of a meal plan.
    """
    def __init__(self,
                 lunch=None,
                 breakfast=None,
                 snack=None,
                 misc=None):
        self.lunch: list[Recipe] = lunch or []
        self.breakfast: list[Recipe] = breakfast or []
        self.snack: list[Recipe] = snack or []
        self.misc: list[Recipe] = misc or []

