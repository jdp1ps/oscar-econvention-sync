from enum import Enum

# Primarily Enums used by activity model


class FinancialImpactEnum(str, Enum):
    """
    3 possibles values for FinancialImpact
    """

    AUCUNE = "Aucune"
    RECETTE = "Recette"
    DEPENSE = "Dépense"


class CurrencyEnum(str, Enum):
    """
    4 possible values for Currency
    """

    EURO = "Euro"
    YENS = "Yens"
    LIVRE = "Livre"
    DOLLARS = "Dollars"


class StatusEnum(int, Enum):
    """
    Possible values for Status
    """

    ACTIF = 101
    BROUILLON = 102
    DEPOSE = 103
    TERMINE = 200
    RESILIE = 201
    ABANDONNE = 250
    REFUSE = 201  # alias pour RESILIE
    CONFLIT = 404  # Pas de statut


# Primarily Enums used by convention model


class OrigineEnum(str, Enum):
    """
    The convention is originated from intern or partner
    """

    INTERNE = "Interne"
    PARTENAIRE = "Partenaire"
