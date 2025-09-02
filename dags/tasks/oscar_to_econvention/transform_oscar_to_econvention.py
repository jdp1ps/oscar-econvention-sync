import json
import logging
from airflow.decorators import task
from pydantic import ValidationError
from models.activity_model import Activity
from models.convention_model import Convention
from utils.aliases import (
    TITRE_ALIAS,
    PORTEUR_ALIAS,
    STRUCTURE_PORTEUR_ALIAS,
    RESPONSABLE_PORTEUR_ALIAS,
    REFERENT_DAJI_ALIAS,
    PARTENAIRE_ALIAS,
    DESCRIPTION_ALIAS,
    TYPE_CONVENTION_ALIAS,
    SOUS_TYPE_CONVENTION_ALIAS,
    DATE_DEMARRAGE_ALIAS,
    TERME_CONVENTION_ALIAS,
    ORIGINE_CONVENTION_ALIAS,
)


@task
def transform_oscar_to_econvention(activities: list[dict]) -> str:
    """Transform data from OSCAR to ECONVENTION by mapping their attributes."""

    activity_list: list[Activity] = [
        Activity.model_validate(activity) for activity in activities
    ]
    convention_list: list[Convention] = []
    errors = []

    for i, activity in enumerate(activity_list):
        mapping = (
            {"Reference": activity.to_reference()}
            | {TITRE_ALIAS: activity.to_titre()}
            | {PORTEUR_ALIAS: activity.to_porteur()}
            | {STRUCTURE_PORTEUR_ALIAS: activity.to_structure()}
            | {RESPONSABLE_PORTEUR_ALIAS: activity.to_responsable_porteur()}
            | {REFERENT_DAJI_ALIAS: activity.to_referent_daji()}
            | {PARTENAIRE_ALIAS: activity.to_partenaire()}
            | {DESCRIPTION_ALIAS: activity.description or ""}
            | {TYPE_CONVENTION_ALIAS: activity.to_convention_type()}
            | {SOUS_TYPE_CONVENTION_ALIAS: activity.to_convention_sous_type()}
            | {ORIGINE_CONVENTION_ALIAS: activity.to_convention_origin()}
            | {DATE_DEMARRAGE_ALIAS: activity.to_date_demarrage()}
            | {TERME_CONVENTION_ALIAS: activity.to_terme_convention()}
            | {"Etape": activity.to_etape()}
        )

        try:
            convention_list.append(Convention.model_validate(mapping))
        except ValidationError as e:
            errors.append({"index": i, "errors": e.errors()})

    if len(errors) > 0:
        logging.error("Some activities failed mapping process: %s", errors)

    results = json.dumps(
        [convention.model_dump(by_alias=True) for convention in convention_list],
        sort_keys=True,
        indent=4,
    )
    return results
