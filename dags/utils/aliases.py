# CONVENTION MODEL FIELDS ALIASES
REFERENCE_ALIAS = "Reference"
TITRE_ALIAS = "Title"
PORTEUR_ALIAS = "Porteur"
STRUCTURE_PORTEUR_ALIAS = "StructurePorteur"
RESPONSABLE_PORTEUR_ALIAS = "ResponsablePorteur"
REFERENT_DAJI_ALIAS = "ReferentDAJI"
PARTENAIRE_ALIAS = "Partenaire"
DESCRIPTION_ALIAS = "DescriptionConvention"
ORIGINE_CONVENTION_ALIAS = "OrigineConvention"
MONTANT_CONVENTION_ALIAS = "MontantConvention"
TYPE_CONVENTION_ALIAS = "TypeConvention"
SOUS_TYPE_CONVENTION_ALIAS = "SousType"
DATE_DEMARRAGE_ALIAS = "DateDemarrage"
TERME_CONVENTION_ALIAS = "TermeConvention"
ETAPE_ALIAS = "Etape"
RECETTES_ALIAS = "Recettes"
DEPENSES_ALIAS = "Depenses"

# ACTIVITY ROLE ALIASES
CHARGEE_DE_VALORISATION_ALIAS = "Chargé(e) de valorisation"

# OTHERS
CONFIRMED_ACTIVITY_ALIAS = "ConfirmedActivities"

# Mapping role CONVENTION/OSCAR

map_role = [(PORTEUR_ALIAS, CHARGEE_DE_VALORISATION_ALIAS)]


def convert_role(alias: str, is_convention_to_oscar: bool) -> str:
    """
    Correspond convention role to activity role and vice versa
    If there's not corresponding aliases in the map
    then it return "".
    """
    start_index = 0 if is_convention_to_oscar else 1
    end_index = 1 if is_convention_to_oscar else 0

    for role in map_role:
        if role[start_index] == alias:
            return role[end_index]
    return ""


def convert_role_for_activity(alias: str) -> str:
    """wrapper of convert_role"""
    return convert_role(alias, is_convention_to_oscar=True)


def convert_role_for_convention(alias: str) -> str:
    """wrapper of convert_role"""
    return convert_role(alias, is_convention_to_oscar=False)
