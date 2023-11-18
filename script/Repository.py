import yaml

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

    ROOT_DIR: Path = Path(__file__).parent
    RECIPE_DIR: Path = ROOT_DIR / "recettes"
    COMPLETE_COOKBOOK_PATH: Path = ROOT_DIR / "cookbook.md"
    MENU_PATH: Path = ROOT_DIR / "menu.md"
    RECIPE_DICT: Dict[str, Path] = {path.stem: path for path in RECIPE_DIR.iterdir() if path.is_file()}
    RECIPE_NAMES: Tuple[str] = tuple([recipe_name for recipe_name in RECIPE_DICT.keys()])

    RECIPE_METADATA_TEMPLATE = {
        Tag.COOKED_DATES: []
    }
    # add a pagebreak web inserted in a markdown document
    PAGEBREAK: str = '\n\n<div style="page-break-after: always;"></div>\n\n'

    def __init__(self):
        self.recipes_metadata = self._read_recipes_metadata()

    def get_recipes_cooked_dates(self):
        recipes_cooked_dates: Dict[str, Any] = {}
        for recipe_name, metadata in self.cookbook_metadata.items():
            recipes_cooked_dates[recipe_name] = metadata[self.COOKED_DATES]
        return recipes_cooked_dates

    @classmethod
    def _read_metadata_from_md(cls, path: Path) -> str | Dict[str, str]:
        """
        :param path: the path to the markdown file containing the metadata
        :return: an empty string if there is no metadata in the file. Otherwise, return a dictionary of the metadata
        """
        lines: str = ""
        metadata_marker: str = "---\n"
        with open(path, 'r') as f:
            line: str = f.readline()
            if line != metadata_marker:  # check if there is metadata in the file
                return ""
            while True:
                line = f.readline()
                if line == metadata_marker:
                    return yaml.safe_load(lines)
                lines += line

    def _read_recipes_metadata(self) -> Dict[str, str | Dict[str, str]]:
        """
        :return: the metadata of all the files in a dictionary
        """
        files_metadata: Dict[str, str | Dict[str, str]] = {}
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
            lines: List[str] = f.readlines()
        recipes_names: List[str] = list(map(lambda line: line.replace("![[", "").replace("]]\n", ""), lines))
        recipes_names = [recipe_name for recipe_name in recipes_names if recipe_name in self.RECIPE_DICT]
        return recipes_names

    def write_menu(self, meal_plan: MealPlan) -> None:
        menu_str: str = f"""# Menu
                
            """
        meal_str: str = """## {}
            
            {}
            
            """
        to_str: Callable[[List[str]], str] = lambda l: "\n".join([f"[[{i}]]" for i in l])

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

        files_wikilinks = [f'![[{file}]]' for file in self.RECIPE_NAMES]

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(self.PAGEBREAK.join(files_wikilinks)))
