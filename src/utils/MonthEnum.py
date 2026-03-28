from enum import Enum


class MonthEnum(Enum):

    JANVIER = "janvier"
    FEVRIER = "février"
    MARS = "mars"
    AVRIL = "avril"
    MAI = "mai"
    JUIN = "juin"
    JUILLET = "juillet"
    AOUT = "août"
    SEPTEMBRE = "septembre"
    OCTOBRE = "octobre"
    NOVEMBRE = "novembre"
    DECEMBRE = "décembre"

    @staticmethod
    def from_number(number: int) -> "MonthEnum":
        match number:
            case 1:
                return MonthEnum.JANVIER
            case 2:
                return MonthEnum.FEVRIER
            case 3:
                return MonthEnum.MARS
            case 4:
                return MonthEnum.AVRIL
            case 5:
                return MonthEnum.MAI
            case 6:
                return MonthEnum.JUIN
            case 7:
                return MonthEnum.JUILLET
            case 8:
                return MonthEnum.AOUT
            case 9:
                return MonthEnum.SEPTEMBRE
            case 10:
                return MonthEnum.OCTOBRE
            case 11:
                return MonthEnum.NOVEMBRE
            case _:
                return MonthEnum.DECEMBRE
