from enum import Enum


class QuantityUnit(Enum):
    KCAL = "kcal"
    G = "g"  # grams
    KG = "kg"  # grams
    ML = "ml"  # milliliters
    CL = "cl"  # centiliters
    L = "l"  # liter
    CC = "cc"  # teaspoon
    CS = "cs"  # soup spoon

    # the following are all interpreted as "piece" units and their ration is stored in ingredients.yaml
    class Piece(Enum):
        PIECE = "piece"
        SLICE = "tranche"
        CLOVE = "gousse"
        PINCH = "pincée"
        BUNCH = "botte"
        BAG = "sachet"
        PACK = "paquet"
        BOUQUET = "bouquet"
        LEAF = "feuille"

    PIECE = Piece

    VOID = ""

    KG_TO_G_RATIO = 1000  # 1kg == 1000g
    ML_TO_G_RATIO = 1
    CL_TO_G_RATIO = 10
    L_TO_G_RATIO = 1000
    CC_TO_G_RATIO = 5
    CS_TO_G_RATIO = 15

    DEFAULT_QUANTITY = 10  # in grams
    DEFAULT_NB_PORTIONS = 4

    # arbitrary value which marginally falsify the calculation, count as almost zero and is odd enough avoid being
    # picked by a legitimate recipe
    INVALID_PIECE_TO_G_RATIO = .314

    @classmethod
    def is_piece_unit(cls, tested_unit: str) -> bool:
        """
        Determine if the given string match a value of the Piece enum
        """

        if tested_unit == QuantityUnit.VOID.value:
            return True
        for piece_unit in [piece.value for piece in QuantityUnit.PIECE.value]:
            if piece_unit in tested_unit:
                return True
        return False

    @staticmethod
    def is_piece_unit_missing_ratio(tested_unit: "QuantityUnit", piece_to_g_ratio: float):
        """
        A quantity of unit Piece may need a piece to grams ratio, different for each ingredient. This ratio can't be
        guessed and is then stored as a base ingredient attribute in ingredients.yaml and is retrieve dynamically for
        proper calculations. This information is not needed for conventional units (not piece one, ie grams,
        centiliters, etc.), so this field is optional in the yaml.

        This method is useful for revealing mistakes in the data loaded in the ingredients.
        """

        return \
            (tested_unit in QuantityUnit.PIECE.value
             and piece_to_g_ratio == QuantityUnit.INVALID_PIECE_TO_G_RATIO.value)

    @staticmethod
    def from_str(unit_str: str):
        if QuantityUnit.is_piece_unit(unit_str):
            return QuantityUnit.PIECE.value.PIECE
        else:
            try:
                return QuantityUnit(unit_str)
            except ValueError:
                return None
