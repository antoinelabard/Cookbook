class MealGenerator:
    """
    MealGenerator: Used to generate a new meal plan, given a certain profile established in advance. This class is
    intended to generate meals plan based on the prior cook history of the cookbook. It uses the cookbook metadata
    cooked dates to determine the least cooked recipes matching the indicated filters, and pick among the candidates
    to return the result.
    """

    def __init__(self, recipe_type: str, opportunity: None | str, nb_lunch: int, nb_breakfast: int, nb_snack: int,
                 nb_appetizers: int):
        self.repository: CookBookRepository = CookBookRepository()

        self.meals: Dict[str, int] = {
            Tag.LUNCH: nb_lunch,
            Tag.BREAKFAST: nb_breakfast,
            Tag.SNACK: nb_snack,
            Tag.APPETIZER: nb_appetizers
        }

        # each filter must be an instance of str, list(str) or None
        self.filters: Dict[str, str | List[str] | None] = {
            Tag.TYPE: recipe_type,
            Tag.OPPORTUNITY: opportunity
        }

    def _match_filters(self, recipe_name: str) -> bool:
        for filter_name in set(self.filters.keys()):
            filter_name = filter_name.value
            if filter_name not in self.repository.recipes_metadata[recipe_name]:
                continue

            if self.filters[filter_name] is None:
                return False

            if self.filters[filter_name] != self.repository.recipes_metadata[recipe_name][filter_name]:
                return False

        return True

    def _match_meal(self, name: str, meal: str) -> bool:
        if Tag.MEAL not in self.repository.recipes_metadata[name]:
            return False
        return self.repository.recipes_metadata[name][Tag.MEAL] == meal

    def generate_meal_plan(self, nb_people: int = 1):
        recipes_names_filtered: List[str] = [name for name in self.repository.RECIPE_NAMES if self._match_filters(name)]
        meal_plan: Dict[str, List[str]] = {}
        for meal, quantity in self.meals.items():
            if quantity == 0:
                meal_plan[meal]: List[str] = []
                continue
            total_quantity: int = quantity * nb_people

            rcp_names: List[str] = [name for name in recipes_names_filtered if self._match_meal(name, meal)]

            if len(rcp_names) == 0:
                continue

            rcp_nm: List[str] = rcp_names.copy()

            meal_plan_per_meal: List[str] = []

            while total_quantity > 0:
                index: int = random.randint(0, len(rcp_nm) - 1)
                meal_plan_per_meal.append(rcp_nm.pop(index))
                total_quantity -= 1

                if len(rcp_nm) == 0:
                    rcp_nm = rcp_names.copy()

            meal_plan[meal] = meal_plan_per_meal
        self.repository.write_menu(
            MealPlan(
                meal_plan[Tag.LUNCH],
                meal_plan[Tag.BREAKFAST],
                meal_plan[Tag.SNACK],
                meal_plan[Tag.APPETIZER]
            )
        )
