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
    DEPOSEE = 103
    MONTAGE = 104
    JUSTIFIEE = 105
    ACCEPTE = 106
    IDENTIFIEE = 107
    EN_COURS_DE_CONVENTIONNEMENT = 108
    ACCEPTE_EN_PHASE_2 = 109
    TERMINE = 200
    RESILIE = 201
    DOSSIER_ABANDONNE = 250
    CLOTURE = 275
    REFUSE = 210
    REFUSE_EN_PHASE_2 = 211
    TRANSFERE = 220
    REORIENTE = 230
    LITIGE = 400
    CONFLIT = 404  # Pas de statut


# Primarily Enums used by convention model


class OrigineEnum(str, Enum):
    """
    The convention is originated from intern or partner
    """

    INTERNE = "Interne"
    PARTENAIRE = "Partenaire"
