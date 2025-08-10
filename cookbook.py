#!/usr/bin/python3

"""
NAME
    cookbook.py - Generate custom meals plans.

SYNOPSIS
    ./cookbook.py [OPTION]...
    python3 cookbook.py [OPTION]...

    cookbook.py can take several arguments:
        - export: create a markdown file containing wikilinks for all the recipes of the cookbook. It can be read using
        Obsidian (https://obsidian.md).
        - "profile": generate a menu following the filters pointed by "profile" (defined in profiles.yaml).
        - ingredient / i: generate the groceries list of the meal plan written in meal plan.md
        - macros: compute and write in macros.md the macros of every recipe in the cookbook

DESCRIPTION
    cookbook.py is intended to generate a random menu matching some filters. Those filters can be given as command line
    arguments, but they also can be given via profiles defined in the script. This script is used to decrease the mental
    load, and make sure that no human mind is involved in the random generation of menus, as it is bad at randomness and
    risks promote some recipes over others. The idea is to randomly pick the recipes matching the provided filters using
    a draw without discount and bet on the equiprobability of each recipe to be chosen in order to statistically select
    every recipe over time.

CONFIGURATION
    cookbook.py needs Python3.11 or higher to work (https://www.python.org/downloads/).

    A profile example is specified in profiles.yaml. It gives most of the use cases to generate a meal plan.

    Profiles are stored in a file as a map for which the keys are the profiles names, and the value is a list of all the
    filters of each profile. You can ask to generate several meal plans by chaining their profiles names in the command
    prompt.

    quantity, recipe-type, meal are mandatory, is_in_season and tags are optional. Concerning tags, for a recipe to be
    selected, it must have all the tags specified, no more or less. if tags is not specified, only recipes with no tag
    will be selected.
"""
import datetime
import logging
import sys

from src.MealPlanBuilder import MealPlanBuilder
from src.data.CookbookRepository import CookbookRepository
from src.utils.Utils import Utils

if __name__ == "__main__":
    logging.basicConfig(
        filename=f'../../../Logs/cookbook/{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.log',
        level=logging.INFO)
    logger = Utils.get_logger()
    repository = CookbookRepository()
    meal_plan_builder = MealPlanBuilder(repository.get_recipes())

    new_export = False
    new_meal_plan = False
    new_ingredients_list = False
    for arg in sys.argv:
        if arg == "export":
            new_export = True

        if arg in ["i", "ingredients"]:
            new_ingredients_list = True
            logger.info("Ingredients list generated.")

        if arg == "macros":
            repository.write_recipes_macros()
            repository.write_to_waistline_json()
            logger.info("Updated and exported the macros of every recipe.")

        if arg in repository.get_profiles().keys():  # if arg is a profile name
            new_meal_plan = True
            for meal_plan_filter in repository.get_profiles()[arg]:
                meal_plan_builder.pick_recipes_with_filter(meal_plan_filter)
            logger.info("Meal plan generated.")

    if new_meal_plan:
        meal_plan = meal_plan_builder.build()
        repository.write_meal_plan(meal_plan)
    if new_ingredients_list:
        repository.write_ingredients()
    if new_export:
        repository.write_complete_cookbook()
