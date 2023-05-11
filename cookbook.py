#!/usr/bin/python3
import copy
import os
import sys
import yaml
import json
from datetime import datetime
import math
import random

APPETIZER_TAG = "appetizer"
BREAKFAST_TAG = "breakfast"
COOKED_DATES_TAG = "cooked dates"
FILTERS_TAG = "filters"
LUNCH_TAG = "lunch"
MEALS_TAG = "meal"
OPPORTUNITY_TAG = "opportunity"
RECIPES_TAG = "recipes"
SNACK_TAG = "snack"
TYPE_TAG = "type"


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
    RECIPE_DIR = "recettes"
    COMPLETE_COOKBOOK_PATH = "livre de recettes.md"
    MENU_PATH = "menu.md"
    RECIPE_METADATA_TEMPLATE = {
        COOKED_DATES_TAG: []
    }

    def __init__(self):
        self.recipes_metadata = self._read_recipes_metadata()

    def get_recipes_names(self):
        """
        :return: A list of the names of the recipes.
        """
        return list(map(
            lambda x: x.split('/')[-1].replace('\n', '').replace('.md', ''),
            os.popen(f'find {self.RECIPE_DIR} -name "*.md"').readlines()
        ))

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
        for recipe_name in self.get_recipes_names():
            file_metadata = self._read_metadata_from_md(f"{self.RECIPE_DIR}/{recipe_name}.md")
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
        recipes_names = list(filter(lambda line: line in self.get_recipes_names(), recipes_names))
        return recipes_names

    def write_menu(self, meal_plan):
        menu_str = f"""# Menu
                
                
            """
        meal_str = """## {}
            
            {}
            
            """
        to_str = lambda l: "\n".join([f"![[{i}]]" for i in l])

        for meal, recipes in meal_plan.items():
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
        wikilinks_str = lambda: '\n'.join(files_wikilinks(sorted(repository.get_recipes_names())))

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(wikilinks_str()))


class MealGenerator:
    """
    MealGenerator: Used to generate a new meal plan, given a certain profile established in advance. This class is
    intended to generate meals plan based on the prior cook history of the cookbook. It uses the cookbook metadata
    cooked dates to determine the least cooked recipes matching the indicated filters, and pick among the candidates
    to return the result.

    profile template: {
        "meals": {
            "lunch": int,
            "breakfast": int,
            "snack": int,
        }
        "filters": {
            "type": str|list(str),
            "opportunity": str|list(str)|None,
        }
    }
    """
    NB_PORTIONS_PER_RECIPE = 4  # I plan to set the number of portions for each recipe
    NB_LUNCHES_PER_DAY = 2
    NB_BREAKFASTS_PER_DAY = 2
    NB_SNACKS_PER_DAY = 1

    week_plan_profile = {
        MEALS_TAG: {
            LUNCH_TAG: math.ceil(
                7 * NB_LUNCHES_PER_DAY / NB_PORTIONS_PER_RECIPE),
            BREAKFAST_TAG: math.ceil(
                3 * NB_BREAKFASTS_PER_DAY / NB_PORTIONS_PER_RECIPE),
            SNACK_TAG: math.ceil(
                3 * NB_SNACKS_PER_DAY / NB_PORTIONS_PER_RECIPE),
        },
        FILTERS_TAG: {
            TYPE_TAG: "meal",
            OPPORTUNITY_TAG: None
        }
    }

    def __init__(self):
        self.repository = CookBookRepository()

    def generate_meal_plan(self, nb_people=1, profile=week_plan_profile):
        recipes_names = repository.get_recipes_names()

        def match_filter(name, flt):
            if profile[FILTERS_TAG][flt] is None and flt not in repository.recipes_metadata[name]:
                return True
            if flt not in repository.recipes_metadata[name]:
                return False
            return repository.recipes_metadata[name][flt] in "None" \
                if profile[FILTERS_TAG][flt] is None \
                else profile[FILTERS_TAG][flt]

        def match_meal(name, meal):
            if MEALS_TAG not in repository.recipes_metadata[name]:
                return False
            return repository.recipes_metadata[name][MEALS_TAG] == meal

        def pick_recipes_per_meal():
            ml_pl = {}
            for meal, quantity in profile[MEALS_TAG].items():
                total_quantity = quantity * nb_people
                rcp_names = copy.copy(recipes_names)

                for flt in profile[FILTERS_TAG]:
                    rcp_names = list(filter(lambda name: match_filter(name, flt), rcp_names))
                rcp_names = list(filter(lambda name: match_meal(name, meal), rcp_names))

                if not rcp_names:
                    break

                rcp_nm = copy.copy(rcp_names)
                meal_plan_per_meal = []
                while total_quantity > 0:
                    index = random.randint(0, len(rcp_nm) - 1)
                    meal_plan_per_meal.append(rcp_nm.pop(index))
                    total_quantity -= 1
                    if not rcp_nm:
                        rcp_nm = copy.copy(rcp_names)
                ml_pl[meal] = meal_plan_per_meal

            return ml_pl

        meal_plan = pick_recipes_per_meal()
        repository.write_menu(meal_plan)


repository = CookBookRepository()
mealGenerator = MealGenerator()

for arg in sys.argv:
    if arg == "export":
        repository.export_complete_cookbook()
    if arg == "plan":
        mealGenerator.generate_meal_plan()
