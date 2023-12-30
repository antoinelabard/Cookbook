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
        if arg in repository.profiles.keys():
            meal_plan_builder.add_recipes(repository.profiles[arg])

