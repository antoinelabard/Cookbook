#!/usr/bin/python3

"""
NAME
    cookbook.py - Generate custom meals.

SYNOPSIS
    ./cookbook.py [OPTION]...

DESCRIPTION
    cookbook.py is intended to generate a random menu matching some filters. Those filters can be given as command line
    arguments, but they also can be given via profiles defines in the script. This script is used to make sure that no
    human mind is involved in the random generation of menus, as it is bad at randomness and risks promote some recipes
    over others. The idea is to randomly pick the recipes matching the provided filters using a draw without discount
    and bet on the equiprobability of each recipe to be chosen in order to statistically select every recipe over time.

CONFIGURATION
    cookbook.py can take several arguments:
        - export: create a markdown file containing wikilinks for all the recipes of the cookbook. It can be read using
        Obsidian (https://obsidian.md).
        - plan=PLAN: generate a menu following the filters pointed by PLAN (defined in the script)
        - filter=VALUE: set a custom filter that the recipes need to match. Here is the list of filters with their
        expected value:
            - type: "meal"|"ingredient"|"inedible"
            - opportunity: None|"cheat-meal"|"party"|"pleasure"
            - lunch: integer
            - breakfast: integer
            - snack: integer
            - appetizer: integer
"""

import copy
import sys
from enum import Enum

import yaml
import math
import random
from pathlib import Path

class Tag(str, Enum):
    APPETIZER_TAG = "appetizer"
    BREAKFAST_TAG = "breakfast"
    COOKED_DATES_TAG = "cooked dates"
    FILTERS_TAG = "filters"
    LUNCH_TAG = "lunch"
    MEALS_TAG = "meal"
    OPPORTUNITY_TAG = "opportunity"
    NB_PEOPLE_TAG = "nb_people"
    PLAN_TAG = "plan"
    RECIPES_TAG = "recipes"
    SNACK_TAG = "snack"
    TYPE_TAG = "type"

class Options(int, Enum):
    NB_PORTIONS_PER_RECIPE = 4  # I plan to set the number of portions for each recipe
    NB_LUNCHES_PER_DAY = 2
    NB_BREAKFASTS_PER_DAY = 2
    NB_SNACKS_PER_DAY = 1


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class CookBookRepository:
    """
    CookBookRepository: Manage the access to the data stored in the cookbook. Any read or write operation must be
        handled by this class. It includes operations to read the general cookbook metadata and the metadata of each of
        the recipes.
    """

    ROOT_DIR = Path(__file__).parent
    RECIPE_DIR = ROOT_DIR / "recettes"
    COMPLETE_COOKBOOK_PATH = ROOT_DIR / "cookbook.md"
    MENU_PATH = ROOT_DIR / "menu.md"
    RECIPE_DICT = {path.stem: path for path in RECIPE_DIR.iterdir() if path.is_file()}
    RECIPE_NAMES = tuple([recipe_name for recipe_name in RECIPE_DICT.keys()])

    RECIPE_METADATA_TEMPLATE = {
        Tag.COOKED_DATES_TAG: []
    }
    # add a pagebreak web inserted in a markdown document
    PAGEBREAK = '\n\n<div style="page-break-after: always;"></div>\n\n'

    def __init__(self):
        self.recipes_metadata = self._read_recipes_metadata()

    def get_recipes_cooked_dates(self):
        recipes_cooked_dates = {}
        for recipe_name, metadata in self.cookbook_metadata.items():
            recipes_cooked_dates[recipe_name] = metadata[self.COOKED_DATES_TAG]
        return recipes_cooked_dates

    def _read_metadata_from_md(self, path):
        """
        :param path: the path to the markdown file containing the metadata
        :return: an empty string if there is no metadata in the file. Otherwise, return a dictionary of the metadata
        """
        lines = ""
        metadata_marker = "---\n"
        with open(path, 'r') as f:
            line = f.readline()
            if line != metadata_marker:  # check if there is metadata in the file
                return ''
            while True:
                line = f.readline()
                if line == metadata_marker:
                    return yaml.safe_load(lines)
                lines += line

    def _read_recipes_metadata(self):
        """
        :return: the metadata of all the files in a dictionary
        """
        files_metadata = {}
        for recipe_name, recipe_path in self.RECIPE_DICT.items():
            file_metadata = self._read_metadata_from_md(recipe_path)
            if file_metadata != '':
                files_metadata[recipe_name] = file_metadata
        return files_metadata

    def read_menu(self):
        """
        Read the menu referred by MENU_PATH and return a list of all the recipes contained in it.
        """
        with open(self.MENU_PATH, 'r') as f:
            recipes_names = f.readlines()
        recipes_names = list(map(lambda line: line.replace("![[", "").replace("]]\n", ""), recipes_names))
        recipes_names = [recipe_name for recipe_name in recipes_names if recipe_name in self.RECIPE_DICT]
        return recipes_names

    def write_menu(self, meal_plan):
        menu_str = f"""# Menu
                
            """
        meal_str = """## {}
            
            {}
            
            """
        to_str = lambda l: self.PAGEBREAK.join([f"![[{i}]]" for i in l])

        for meal, recipes in meal_plan.__dict__.items():
            menu_str += meal_str.format(meal, to_str(recipes))
        menu_str = menu_str.replace("    ", "")
        print(menu_str)
        with open(self.MENU_PATH, 'w') as f:
            f.write(menu_str)

    def export_complete_cookbook(self):
        """
        create a document containing quotes of the recipes contained in the cookbook.
        """

        complete_cookbook_template = """# Livre de recettes
        
            {}""".replace("    ", "")

        files_wikilinks = lambda files_list: \
            map(lambda file: '![[{}]]'.format(file.split('/')[-1].replace('.md\n', '')), files_list)
        wikilinks_str = lambda: self.PAGEBREAK.join(files_wikilinks(sorted(self.get_recipes_names())))

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(wikilinks_str()))


class MealPlan:
    def __init__(self, lunch_list, breakfast_list, snack_list, appetizer_list):
        self.lunch = lunch_list
        self.breakfast = breakfast_list
        self.snack = snack_list
        self.appetizer = appetizer_list


class MealGenerator:
    """
    MealGenerator: Used to generate a new meal plan, given a certain profile established in advance. This class is
    intended to generate meals plan based on the prior cook history of the cookbook. It uses the cookbook metadata
    cooked dates to determine the least cooked recipes matching the indicated filters, and pick among the candidates
    to return the result.
    """

    def __init__(self, recipe_type, opportunity, nb_lunch, nb_breakfast, nb_snack, nb_appetizers):
        self.repository = CookBookRepository()

        self.meals = {
            Tag.LUNCH_TAG: nb_lunch,
            Tag.BREAKFAST_TAG: nb_breakfast,
            Tag.SNACK_TAG: nb_snack,
            Tag.APPETIZER_TAG: nb_appetizers
        }

        # each filter must be an instance of str, list(str) or None
        self.filters = {
            Tag.TYPE_TAG: recipe_type,
            Tag.OPPORTUNITY_TAG: opportunity
        }

    def _match_filters(self, recipe_name):
        for flt in set(self.filters.keys()):
            if self.filters[flt] is not None and flt not in self.repository.recipes_metadata[recipe_name]:
                return False
            if flt in self.repository.recipes_metadata[recipe_name]:
                if self.filters[flt] != self.repository.recipes_metadata[recipe_name][flt]:
                    return False
        return True

    def _match_meal(self, name, meal):
        if Tag.MEALS_TAG not in self.repository.recipes_metadata[name]:
            return False
        return self.repository.recipes_metadata[name][Tag.MEALS_TAG] == meal

    def generate_meal_plan(self, nb_people=1):
        recipes_names_filtered = \
            list(filter(lambda name: self._match_filters(name), self.repository.RECIPE_NAMES))
        meal_plan = {}
        for meal, quantity in self.meals.items():
            if quantity == 0:
                meal_plan[meal] = []
                continue
            total_quantity = quantity * nb_people
            rcp_names = copy.copy(recipes_names_filtered)

            rcp_names = list(filter(lambda name: self._match_meal(name, meal), rcp_names))

            if not rcp_names:
                continue

            rcp_nm = copy.copy(rcp_names)
            meal_plan_per_meal = []
            while total_quantity > 0:
                index = random.randint(0, len(rcp_nm) - 1)
                meal_plan_per_meal.append(rcp_nm.pop(index))
                total_quantity -= 1
                if not rcp_nm:
                    rcp_nm = copy.copy(rcp_names)
            meal_plan[meal] = meal_plan_per_meal
        self.repository.write_menu(
            MealPlan(
                meal_plan[Tag.LUNCH_TAG],
                meal_plan[Tag.BREAKFAST_TAG],
                meal_plan[Tag.SNACK_TAG],
                meal_plan[Tag.APPETIZER_TAG]
            )
        )


def process_arguments():
    args = {
        Tag.TYPE_TAG: Tag.MEALS_TAG,
        Tag.LUNCH_TAG: 0,
        Tag.BREAKFAST_TAG: 0,
        Tag.SNACK_TAG: 0,
        Tag.APPETIZER_TAG: 0,
        Tag.OPPORTUNITY_TAG: None,
        Tag.NB_PEOPLE_TAG: 1
    }
    for arg in sys.argv:
        if "export" in arg:
            CookBookRepository().export_complete_cookbook()
            return
        if "plan" in arg:
            plan = arg.split('=')[-1]
            if plan == "week":
                args[Tag.TYPE_TAG] = Tag.MEALS_TAG
                args[Tag.OPPORTUNITY_TAG] = None
                args[Tag.LUNCH_TAG] = math.ceil(7 * Options.NB_LUNCHES_PER_DAY / Options.NB_PORTIONS_PER_RECIPE)
                args[Tag.BREAKFAST_TAG] = math.ceil(3 * Options.NB_LUNCHES_PER_DAY / Options.NB_PORTIONS_PER_RECIPE)
                args[Tag.SNACK_TAG] = math.ceil(3 * Options.NB_LUNCHES_PER_DAY / Options.NB_PORTIONS_PER_RECIPE)
                args[Tag.APPETIZER_TAG] = 0
        if '=' in arg:
            s = arg.split('=')
            args[s[0]] = s[-1]
    MealGenerator(
        recipe_type=args[Tag.TYPE_TAG],
        opportunity=args[Tag.OPPORTUNITY_TAG],
        nb_lunch=int(args[Tag.LUNCH_TAG]),
        nb_breakfast=int(args[Tag.BREAKFAST_TAG]),
        nb_snack=int(args[Tag.SNACK_TAG]),
        nb_appetizers=int(args[Tag.APPETIZER_TAG]),
    ).generate_meal_plan(int(args[Tag.NB_PEOPLE_TAG]))


if __name__ == "__main__":
    process_arguments()
