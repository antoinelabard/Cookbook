from enum import Enum


class QuantityUnit(Enum):
    G = "g"  # grams
    KG = "kg"  # grams
    ML = "ml"  # milliliters
    CL = "cl"  # centiliters
    L = "l"  # liter
    CC = "cc"  # teaspoon
    CS = "cs"  # soup spoon

    # the following are all interpreted as "piece" units and their ration is stored in macros.yaml
    class Piece(Enum):
        PIECE = "piece"
        SLICE = "tranche"
        CLOVE = "gousse"
        PINCH = "pincée"
        BUNCH = "botte"
        BAG = "sachet"
        PACK = "paquet"
        BOUQUET = "bouquet"
        VOID = ""
    PIECE = Piece

    KG_TO_G_RATIO = 1000  # 1kg == 1000g
    CL_TO_G_RATIO = 10
    ML_TO_G_RATIO = 1
    CC_TO_G_RATIO = 5
    CS_TO_G_RATIO = 15
