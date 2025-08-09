from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import yaml

from src.MealPlanBuilder import MealPlanBuilder
from src.MealPlanFilter import MealPlanFilter
from src.entities import MealPlan
from src.entities.Ingredient import Ingredient
from src.entities.Macros import Macros
from src.entities.Recipe import Recipe
from src.utils.Constants import Constants
from src.utils.QuantityUnit import QuantityUnit
from src.utils.Utils import Utils


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

    ROOT_DIR: Path = Path(__file__).parent.parent.parent
    RECIPE_DIR: Path = ROOT_DIR / "recettes"
    COMPLETE_COOKBOOK_PATH: Path = ROOT_DIR / "cookbook.md"
    MENU_PATH: Path = ROOT_DIR / "meal plan.md"
    INGREDIENTS_PATH: str = ROOT_DIR / "ingredients.md"
    PROFILES_PATH = ROOT_DIR / "profiles.yaml"
    BASE_INGREDIENTS_PATH = ROOT_DIR / "ingredients.yaml"
    MACROS_PATH = ROOT_DIR / "macros.md"

    def __init__(self):
        self._logger = Utils.get_logger()
        self._logger.addHandler(logging.StreamHandler())
        self._base_ingredients = self._read_base_ingredients()
        self._recipes_paths: list[Path] = [path for path in self.RECIPE_DIR.iterdir() if path.is_file()]
        self._recipes: list[Recipe] = self._read_recipes()
        self._recipes_names: list[str] = list(map(lambda recipe: recipe.get_name(), self._recipes))
        self._profiles: dict[str, list[MealPlanFilter]] = self._read_profiles()

    def get_recipes(self) -> list[Recipe]:
        return self._recipes

    def get_profiles(self) -> dict[str, list[MealPlanFilter]]:
        return self._profiles

    def write_meal_plan(self, meal_plan: MealPlan) -> None:
        """
        Write down in meal_plan.md the provided MealPlan.
        :param meal_plan: the MealPlan to write down
        """

        with open(self.MENU_PATH, 'w') as f:
            f.write(meal_plan.to_str())

    def write_complete_cookbook(self) -> None:
        """
        Create a document containing quotes of the recipes contained in the cookbook.
        """

        page_break: str = '\n\n<div style="page-break-after: always;"></div>\n\n'
        complete_cookbook_template: str = "# Livre de recettes\n\n{}"
        files_wikilinks = sorted([f'![[{path.name}]]' for path in self._recipes_paths])

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(page_break.join(files_wikilinks)))

    def write_ingredients(self):
        """
        Write the ingredients of the given Recipe list in the file pointed by INGREDIENTS_PATH.
        The ingredients are categorized by aisle following the convention described in INGREDIENTS_AISLES_PATH.
        """

        ingredients_by_aisle = self._read_meal_plan().get_ingredients_list_by_aisle()
        output = []

        for aisle, ingredients in ingredients_by_aisle.items():
            output.append(f"- [ ] {aisle}")
            for ingredient in sorted(ingredients):
                output.append(f"  - [ ] {ingredient}")

        with open(self.INGREDIENTS_PATH, 'w') as f:
            f.write("\n".join(output))

    def write_recipes_macros(self):
        """
        Write in the file macros.yaml the macros of all the recipes, as a Markdown table
        """

        output = [
            "| Recette | Énergie | Protéines | Lipides | Glucides |",
            "|:--------|:-------:|:---------:|:-------:|:--------:|"]

        for recipe in sorted(self._recipes, key=lambda rcp: rcp.get_name()):
            output.append(recipe.get_macros_as_markdown_table_line())

        with open(self.MACROS_PATH, 'w') as f:
            f.write("\n".join(output))

    def _read_base_ingredients(self) -> list[Ingredient]:
        """
        :return: the list of all the base ingredients stored in ingredients.yaml
        """

        with open(self.BASE_INGREDIENTS_PATH, 'r') as f:
            lines = f.readlines()

        ingredients: list[Ingredient] = []
        for ingredient_str, attributes in yaml.safe_load("".join(lines)).items():
            macros = Macros(
                energy=attributes[Constants.Macros.ENERGY],
                proteins=attributes[Constants.Macros.PROTEINS],
                lipids=attributes[Constants.Macros.LIPIDS],
                carbs=attributes[Constants.Macros.CARBS],
            )
            ingredients.append(Ingredient(
                ingredient_str,
                macros=macros,
                piece_to_g_ratio=attributes[
                    Constants.Macros.PIECE_TO_G_RATIO]
                if Constants.Macros.PIECE_TO_G_RATIO in attributes.keys()
                else QuantityUnit.INVALID_PIECE_TO_G_RATIO.value,
                aisle=attributes[Constants.AISLE] if Constants.AISLE in attributes else None
            ))

        return ingredients

    def _load_ingredient_object_from_recipe_line(self, ingredient_line: str, recipe_name: str) \
            -> Optional[Ingredient | Recipe]:
        """
        Take an ingredient line from a Markdown recipe (ie 'ingredient' : quantity unit) and load an Ingredient
        object by matching its name with the base ingredients.
        """

        recipe_ingredient_name, recipe_ingredient_quantity, recipe_ingredient_quantity_unit \
            = Utils.extract_name_and_quantity_from_ingredient_line(ingredient_line)

        kept_ingredient = Ingredient.from_name(recipe_ingredient_name, self._base_ingredients)
        if kept_ingredient is None:
            self._logger.warning(
                f"no base ingredient candidate for for ingredient name {recipe_ingredient_name} "
                f"in recipe {recipe_name}")
            return None

        kept_ingredient.set_name(recipe_ingredient_name)
        kept_ingredient.set_quantity(recipe_ingredient_quantity)
        kept_ingredient.set_quantity_unit(QuantityUnit.from_str(recipe_ingredient_quantity_unit))
        kept_ingredient.compute_macros_from_quantity()
        kept_ingredient.set_ingredient_line(ingredient_line)

        # various logging if something went wrong or seem suspicious
        if not kept_ingredient.get_quantity_unit():
            self._logger.warning(
                f"unit {recipe_ingredient_quantity_unit} not recognised in recipe {recipe_name}")
            return None
        if QuantityUnit.is_piece_unit_missing_ratio(
                kept_ingredient.get_quantity_unit(),
                kept_ingredient.get_piece_to_g_ratio()):
            self._logger.warning(
                f"Suspicious piece_to_g_ratio of {kept_ingredient.get_piece_to_g_ratio()} found for ingredient "
                f"{kept_ingredient.get_name()} in recipe {recipe_name}, which may need a custom one written in "
                f"{self.BASE_INGREDIENTS_PATH}")
        if kept_ingredient.get_macros().get_energy() == 0:
            self._logger.warning(
                f"the ingredient {kept_ingredient.get_name()} has one or many of its macros set to 0 in recipe {recipe_name}")

        return kept_ingredient

    def _load_ingredients_from_recipe(self, ingredients_str: list[str], recipe_name: str) -> list[Ingredient | Recipe]:
        """
        :returns a list of Ingredients objects based on the ingredients in a Markdown recipe
        """

        ingredients_str = [ingredient.strip() for ingredient in ingredients_str]
        ingredients_str = [ingredient.replace("- [ ] ", "") for ingredient in ingredients_str]
        ingredients_str = [ingredient.replace("\n", "") for ingredient in ingredients_str]

        ingredients: list[Ingredient | Recipe] = []
        for recipe_ingredient_str in ingredients_str:
            # the given ingredient is, in fact, a recipe
            if "[[" in recipe_ingredient_str and "]]" in recipe_ingredient_str:
                _, recipe_ingredient_quantity, _ = \
                    Utils.extract_name_and_quantity_from_ingredient_line(recipe_ingredient_str)

                ingredient_recipe_name = (recipe_ingredient_str
                .split("[[")[-1]
                .split("]]")[0])

                kept_recipe = self._read_recipe_from_file(
                    next(filter(lambda path, name=ingredient_recipe_name: name in path.name, self._recipes_paths)))
                if recipe_ingredient_quantity:
                    kept_recipe.compute_macros(recipe_ingredient_quantity)
                ingredients.append(kept_recipe)
                continue
            kept_ingredient = self._load_ingredient_object_from_recipe_line(recipe_ingredient_str, recipe_name)
            if kept_ingredient: ingredients.append(kept_ingredient)

        return ingredients

    @staticmethod
    def _get_sections_from_recipe(lines: list[str]) -> Optional[tuple[list[int], list[int], list[int]]]:
        """
        Every recipe contains at least three sections: the metadata, the ingredients list and the instructions. We need
        to distinguish them in order to properly read the relevant information inside.

        :param lines: a list containing each line of a recipe Markdown file
        :return: the indexes delimiting the different sections if the recipe is properly formatted, None otherwise
        """

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

        return metadata_range, ingredients_range, instructions_range

    def _read_recipe_from_file(self, path: Path) -> Optional[Recipe]:
        """
        :param path: the path to the Markdown file containing the recipe
        :return: a recipe object if one of this name actually exists, else None
        """

        with open(path, 'r') as f:
            lines = f.readlines()

        metadata_range, ingredients_range, instructions_range = self._get_sections_from_recipe(lines)

        metadata: dict[str, str | list[str]] = yaml.safe_load("".join(lines[metadata_range[0]:metadata_range[1]]))

        ingredients = self._load_ingredients_from_recipe(lines[ingredients_range[0]:ingredients_range[1]], path.name)

        instructions = lines[instructions_range[0]:instructions_range[1]]
        instructions = [instruction.replace("\n", "") for instruction in instructions]

        recipe = Recipe(
            name=path.name.replace(".md", ""),
            recipe_type=metadata[Constants.RECIPE_TYPE],
            ingredients=ingredients,
            instructions=instructions,
            date_added=metadata[Constants.DATE_ADDED] if Constants.DATE_ADDED in metadata.keys() else None,
            source=metadata[Constants.SOURCE] if Constants.SOURCE in metadata.keys() else None,
            meal=metadata[Constants.Meal.MEAL] if Constants.Meal.MEAL in metadata.keys() else None,
            seasons=metadata[Constants.Season.SEASON] if Constants.Season.SEASON in metadata.keys() else None,
            tags=metadata[Constants.TAGS] if Constants.TAGS in metadata.keys() else None,
            portions=metadata[
                Constants.Macros.PORTIONS] if Constants.Macros.PORTIONS in metadata.keys() else QuantityUnit.DEFAULT_NB_PORTIONS.value
        )
        recipe.compute_macros()

        return recipe

    def _read_recipes(self) -> list[Recipe]:
        """
        :return: the list of all the recipes in the cookbook
        """

        recipes: list[Recipe] = []
        for recipe_path in self._recipes_paths:
            recipe = self._read_recipe_from_file(recipe_path)
            if recipe: recipes.append(recipe)

        return recipes

    @staticmethod
    def _load_filter_from_profile(profile_filter: dict) -> MealPlanFilter:
        """
        :return: a MealPlanFilter with the data of the dict loaded from profiles.yaml
        """

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
        return MealPlanFilter(
            profile_filter[Constants.QUANTITY],
            profile_filter[Constants.RECIPE_TYPE],
            meal,
            is_in_season,
            tags,
        )

    def _read_profiles(self) -> dict[str, list[MealPlanFilter]]:
        """
        Retrieve the profiles from "profiles.yaml" and present the data as a dictionary for which the keys are the
        profiles names and the values are a list of MealPlanFilters for each profile.
        """

        with open(self.PROFILES_PATH, "r") as f:
            data = yaml.safe_load("\n".join(f.readlines()))

        profiles = {}
        for profile, profile_filters in data.items():
            profiles[profile] = []
            for profile_filter in profile_filters:
                profiles[profile].append(self._load_filter_from_profile(profile_filter))

        return profiles

    def _read_meal_plan(self) -> MealPlan:
        """
        Read the recipes names listed in the menu file pointed by MENU_PATH.
        """

        with open(self.MENU_PATH, 'r') as f:
            lines = f.readlines()

        meal_plan_builder = MealPlanBuilder(self._recipes)

        current_meal_selector = Constants.Meal.LUNCH

        for line in lines:
            if f"# {Constants.Meal.BREAKFAST}" in line:
                current_meal_selector = Constants.Meal.BREAKFAST
                continue
            elif f"# {Constants.Meal.LUNCH}" in line:
                current_meal_selector = Constants.Meal.LUNCH
                continue
            elif f"# {Constants.Meal.SNACK}" in line:
                current_meal_selector = Constants.Meal.SNACK
                continue

            recipe_candidate = (line
                                .split("[[")[1]
                                .split("]]")[0]
                                if "[[" in line and "]]" in line else "")
            if recipe_candidate in self._recipes_names:
                meal_plan_builder.add_recipe(
                    current_meal_selector,
                    Recipe.filter_recipe_by_name(recipe_candidate, self._recipes))

        return meal_plan_builder.build()
