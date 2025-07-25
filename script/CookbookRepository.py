from __future__ import annotations

from pathlib import Path

import yaml

from script import MealPlan
from script.Constants import Constants
from script.MealPlanFilter import MealPlanFilter
from script.Recipe import Recipe


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class CookbookRepository:
    """
    CookBookRepository: Manage the access to the data stored in the cookbook. Any read or write operation must be
    handled by this class. It includes operations to read the general cookbook metadata and the metadata of each of
    the recipes.
    """

    ROOT_DIR: Path = Path(__file__).parent.parent
    RECIPE_DIR: Path = ROOT_DIR / "recettes"
    COMPLETE_COOKBOOK_PATH: Path = ROOT_DIR / "cookbook.md"
    MENU_PATH: Path = ROOT_DIR / "menu.md"
    INGREDIENTS_PATH: str = ROOT_DIR / "ingredients.md"
    PROFILES_PATH = ROOT_DIR / "profiles.yaml"
    INGREDIENTS_AISLES_PATH = ROOT_DIR / "ingredients.yaml"

    LINK_DELIMITER_OPEN = "[["
    LINK_DELIMITER_CLOSED = "]]"
    # used to avoid infinite loops
    PSEUDO_LINK_DELIMITER_OPEN = "€€"
    PSEUDO_LINK_DELIMITER_CLOSED = "$$"

    SOURCE_RECIPE_SEPARATOR = " ---> "

    def __init__(self):
        self.recipes = self._read_recipes()
        self.profiles = self._read_profiles()
        self.ingredients_aisles = self._read_ingredients_aisles()

    def _get_recipes_paths(self) -> list[Path]:
        """
        :return: the list of the absolute paths of all the recipes in the cookbook
        """
        return [path for path in self.RECIPE_DIR.iterdir() if path.is_file()]

    @classmethod
    def _load_recipe_from_file(cls, path: Path) -> Recipe | None:
        """
        :param path: the path to the markdown file containing the metadata
        :return: a recipe object if one of this name actually exists, else None
        """
        with open(path, 'r') as f:
            lines = f.readlines()

        metadata_delimiter: str = "---\n"
        ingredients_delimiter: str = "## Ingrédients"
        instructions_delimiter: str = "## Préparation"

        # the following tests check if it contains the standard section delimiters, so is formatted as a recipe
        joined_lines: str = "".join(lines)
        if metadata_delimiter not in joined_lines:
            return None
        if ingredients_delimiter not in joined_lines:
            return None
        if instructions_delimiter not in joined_lines:
            return None

        # split the file in 3 sections
        # the ranges are meant to remove unwanted lines and dissociate the metadata, the ingredients list and the
        #   instructions
        metadata_range: list[int] = [1]  # the metadata is at the beginning of the file
        ingredients_range: list[int] = []
        instructions_range: list[int] = []
        for i in range(1, len(lines)):
            if metadata_delimiter in lines[i]:
                metadata_range.append(i)
            if ingredients_delimiter in lines[i]:
                ingredients_range.append(i + 2)
            if instructions_delimiter in lines[i]:
                ingredients_range.append(i - 1)
                instructions_range.append(i + 2)
        instructions_range.append(len(lines))

        metadata: dict[str, str | list[str]] = yaml.safe_load("".join(lines[metadata_range[0]:metadata_range[1]]))

        ingredients = lines[ingredients_range[0]:ingredients_range[1]]
        ingredients = [ingredient.strip() for ingredient in ingredients]
        ingredients = [ingredient.replace("- [ ] ", "") for ingredient in ingredients]
        ingredients = [ingredient.replace("\n", "") for ingredient in ingredients]

        instructions = lines[instructions_range[0]:instructions_range[1]]
        instructions = [instruction.replace("\n", "") for instruction in instructions]

        recipe = Recipe(
            path.name.replace(".md", ""),
            metadata[Constants.RECIPE_TYPE],
            ingredients,
            instructions,
            metadata[Constants.DATE_ADDED] if Constants.DATE_ADDED in metadata.keys() else None,
            metadata[Constants.SOURCE] if Constants.SOURCE in metadata.keys() else None,
            metadata[Constants.Meal.MEAL] if Constants.Meal.MEAL in metadata.keys() else None,
            metadata[Constants.Season.SEASON].split(", ") if Constants.Season.SEASON in metadata.keys() else None,
            metadata[Constants.TAGS].split(", ") if Constants.TAGS in metadata.keys() else None
            metadata[Constants.Season.SEASON] if Constants.Season.SEASON in metadata.keys() else None,
            metadata[Constants.TAGS] if Constants.TAGS in metadata.keys() else None
        )

        return recipe

    def _read_recipes(self) -> list[Recipe]:
        """
        :return: the list of all the recipes in the cookbook
        """
        recipes: list[Recipe] = []
        for recipe_path in self._get_recipes_paths():
            recipe = self._load_recipe_from_file(recipe_path)
            if recipe is not None:
                recipes.append(recipe)
        return recipes

    def _read_profiles(self) -> dict[str, list[MealPlanFilter]]:
        """
        Retrieve the profiles from "profiles.yaml" and present the data as an dictionary for which the keys are the
        profiles names and the values are a list of MealPlanFilters for each profile.
        :return: the dictionary of profiles
        """
        with open(self.PROFILES_PATH, "r") as f:
            data = yaml.safe_load("\n".join(f.readlines()))
        profiles = {}
        for profile, profile_filters in data.items():
            profiles[profile] = []
            for profile_filter in profile_filters:
                meal = None
                is_in_season = False
                tags = None
                if Constants.Meal.MEAL in profile_filter.keys():
                    meal = profile_filter[Constants.Meal.MEAL]
                if Constants.Season.IS_IN_SEASON in profile_filter.keys():
                    is_in_season = profile_filter[Constants.Season.IS_IN_SEASON]
                if Constants.TAGS in profile_filter.keys():
                    tags = profile_filter[Constants.TAGS]
                    if type(tags) is str: tags = [tags]
                meal_plan_filter = MealPlanFilter(
                    profile_filter[Constants.QUANTITY],
                    profile_filter[Constants.RECIPE_TYPE],
                    meal,
                    is_in_season,
                    tags,
                )
                profiles[profile].append(meal_plan_filter)

        return profiles

    def _read_recipes_from_menu(self) -> list[Recipe]:
        """
        Read the recipes names listed in the menu file pointed by MENU_PATH
        :return: a list of recipes names
        """
        with open(self.MENU_PATH, 'r') as f:
            lines = f.readlines()

        # filter the recipes cited in the names list
        names = list(map(lambda name: name.split(self.LINK_DELIMITER_OPEN)[1].split(self.LINK_DELIMITER_CLOSED)[0] if self.LINK_DELIMITER_OPEN in name else "", lines))
        return list(filter(lambda recipe: recipe.name in names, self.recipes))

    def _read_ingredients_aisles(self) -> dict[list[str]]:
        """
        read from the file INGREDIENTS_AISLES_PATH the associations between ingredients and aisles
        :return: a dict for which the keys are the aisles and the values are a list of ingredients
        """
        with open(self.INGREDIENTS_AISLES_PATH, 'r') as f:
            lines = f.readlines()
        return yaml.safe_load("".join(lines))

    def write_meal_plan(self, meal_plan: MealPlan) -> None:
        """
        Write down in a file the provided MealPlan.
        :param meal_plan: the MealPlan to write down
        """
        meals_links: list[str] = []
        for meal, recipes in meal_plan.__dict__.items():
            recipes_links = "\n".join([f"- [ ] [[{recipe.name}]]" for recipe in recipes])
            if recipes_links:
                meals_links.append(f"# {meal}\n\n{recipes_links}")
        with open(self.MENU_PATH, 'w') as f:
            f.write("\n\n".join(meals_links))

    def export_complete_cookbook(self) -> None:
        """
        Create a document containing quotes of the recipes contained in the cookbook.
        """
        page_break: str = '\n\n<div style="page-break-after: always;"></div>\n\n'
        complete_cookbook_template: str = "# Livre de recettes\n\n{}"
        files_wikilinks = sorted([f'![[{path.name}]]' for path in self._get_recipes_paths()])

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(page_break.join(files_wikilinks)))

    def write_ingredients(self):
        """
        Write the ingredients of the given Recipe list in the file pointed by INGREDIENTS_PATH.
        The ingredients are categorized by aisle following the convention described in INGREDIENTS_AISLES_PATH
        """

        # retrieve in a single list all the ingredients from all the recipes in the menu. Add the recipe name as a suffix for each
        menu_ingredients: list[str] = []
        for recipe in self._read_recipes_from_menu():
            recipe_ingredients: list[str] = [f"{igr}<sup>{self.SOURCE_RECIPE_SEPARATOR}€€{recipe.name}$$</sup>" for igr in recipe.ingredients]
            menu_ingredients = menu_ingredients + recipe_ingredients

        # look for inner recipes in the ingredients list. The list of ingredient will grow with the new inner ones. They are added at the end so that the iteration scans all of them recursively
        # also concatenate the recipe's call stack as breadcrumbs
        index: int = 0
        for ingredient in menu_ingredients:
            if self.LINK_DELIMITER_OPEN in ingredient and self.LINK_DELIMITER_CLOSED in ingredient:
                potential_recipe_name: str = ingredient.split(self.LINK_DELIMITER_OPEN)[1].split(self.LINK_DELIMITER_CLOSED)[0]

                inner_recipe: list[Recipe] = list(filter(lambda rcp: rcp.name in potential_recipe_name, self.recipes))
                inner_recipe: Recipe = inner_recipe[0] if inner_recipe else None
                if inner_recipe is not None:
                    source_recipe: str = (menu_ingredients[index]
                                          .split(f"<sup>{self.SOURCE_RECIPE_SEPARATOR}")[0]
                                          .replace("[[", "€€")
                                          .replace("]]", "$$"))

                    inner_recipe_ingredients: list[str] = [f"{sub_ingredient}<sup>{self.SOURCE_RECIPE_SEPARATOR}=={source_recipe}==</sup>"
                                                  for sub_ingredient in inner_recipe.ingredients]
                    [menu_ingredients.append(sub_ingredient) for sub_ingredient in inner_recipe_ingredients]
            index += 1

        # replace the pseudo wikilinks delimiters by real ones
        menu_ingredients: list[str] = [menu_ingredient.replace(self.PSEUDO_LINK_DELIMITER_OPEN, self.LINK_DELIMITER_OPEN).replace(self.PSEUDO_LINK_DELIMITER_CLOSED, self.LINK_DELIMITER_CLOSED)
                                       for menu_ingredient in menu_ingredients]

        # used to make lowercase string comparisons without altering the case when writing down the ingredients. Also remove the breadcrumbs temporarily
        menu_ingredients_lowercase: list[str] = [ingredient.lower().split(self.SOURCE_RECIPE_SEPARATOR)[0][0:-5] for ingredient in menu_ingredients]
        ingredients_aisles: dict[str, list[str]] = {aisle: [] for aisle in self.ingredients_aisles.keys()}
        i: int = 0
        while i < len(menu_ingredients):
            ingredient_lowercase: str = menu_ingredients_lowercase[i]
            aisles_candidates: dict[
                str, str] = {}  # sometimes, multiple reference ingredients match the tested recipe ingredient. This dictionary is used to enumerate those candidates and pick the winner among them
            for aisle in self.ingredients_aisles.keys():
                ref_ingredients_by_aisle: list[str] = sorted(self.ingredients_aisles[aisle], key=lambda a: -len(a))
                for reference_ingredient in ref_ingredients_by_aisle:
                    reference_ingredient: str = reference_ingredient.lower()
                    if reference_ingredient in ingredient_lowercase:
                        aisles_candidates[reference_ingredient] = aisle
            if not aisles_candidates:
                i += 1
                continue
            aisle_winner: str = aisles_candidates[max(aisles_candidates.keys(), key=len)]  # the winner is the reference ingredient with the longer name (it's better to match "chorizo" than "riz")
            ingredients_aisles[aisle_winner].append(menu_ingredients.pop(i))
            menu_ingredients_lowercase.pop(i)
        ingredients_aisles["Unclassified"] = menu_ingredients

        # prepare the final string, with all the ingredients classified by their aisle
        menu_ingredients: list[str] = []
        for aisle in ingredients_aisles.keys():
            if not ingredients_aisles[aisle]:
                continue
            ingredients_aisles[aisle].sort()
            menu_ingredients.append(f"- [ ] {aisle} :\n" + "\n".join([f"    - [ ] {ingredient}" for ingredient in ingredients_aisles[aisle]]))

        with open(self.INGREDIENTS_PATH, 'w') as f:
            f.write("\n".join(menu_ingredients))
