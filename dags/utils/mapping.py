import datetime
import time

map_convention = {
    "Reference": "uid",
    "Titre": "label",
    "Porteur": "persons",
    "Créateur": "persons",
    "LecteursComplémentaires": "persons",
    "Sticture Porteur": "organizations",
    "Partenaire": "organizations",
    "DescriptionConvention": "description",
    "Origine de la convention": "AttributeNotHere",
    "Type de la convention": "AttributeNotHere",
    "SousType": "type",
    "DateDemarrage": "datestart",
    "TermeConvention": "dateend",
    "Depenses": "financialImpact",
    "Recettes": "financialImpact",
    "MontantConvention": "amount",
    "Etape": "milestones",
}

todays_date = datetime.date.fromtimestamp(time.time())
DATE_IN_ISOFORMAT = str(todays_date.isoformat())
defaults = {
    "acronym": DATE_IN_ISOFORMAT,
    "projectlabel": DATE_IN_ISOFORMAT,
    "financialImpact": "Aucune",
    "type": "",
    "pfi": "",
    "organizations": {},
    "persons": {},
    "milestones": [],
    "status": 200,
}

oscar_special_keys = {"persons", "organizations"}
