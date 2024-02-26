#!/usr/bin/python3

"""
NAME
    cookbook.py - Generate custom meals plans.

SYNOPSIS
    ./cookbook.py [OPTION]...

DESCRIPTION
    cookbook.py is intended to generate a random menu matching some filters. Those filters can be given as
    command line arguments, but they also can be given via profiles defined in the script. This script is used to
    decrease the mental load, and make sure that no human mind is involved in the random generation of menus,
    as it is bad at randomness and risks promote some recipes over others. The idea is to randomly pick the recipes
    matching the provided filters using a draw without discount and bet on the equiprobability of each recipe to be
    chosen in order to statistically select every recipe over time.

CONFIGURATION
    cookbook.py can take several arguments:
        - export: create a markdown file containing wikilinks for all the recipes of the cookbook. It can be read using
        Obsidian (https://obsidian.md).
        - [profile]: generate a menu following the filters pointed by "profile" (defined in profiles.yaml)

    A profile example is specified in profiles.yaml. It gives most use cases to generate a meal plan. profiles are
    stored in a file as a hashmap for which the keys are the profiles names, and the value is a list of all the
    filters of each profile. You can ask to generate several meal plans by chaining their profiles names in the command
    prompt.
"""

from __future__ import annotations

import sys

from script.CookbookRepository import CookbookRepository
from script.MealPlanBuilder import MealPlanBuilder

if __name__ == "__main__":
    repository = CookbookRepository()
    meal_plan_builder = MealPlanBuilder()

    for arg in sys.argv:
        if arg == "export":
            CookbookRepository().export_complete_cookbook()
        if arg in repository.profiles.keys():  # if arg is a profile name
            [meal_plan_builder.add_recipes(meal_plan_filter) for meal_plan_filter in repository.profiles[arg]]

    meal_plan = meal_plan_builder.build()
    repository.write_meal_plan(meal_plan)
