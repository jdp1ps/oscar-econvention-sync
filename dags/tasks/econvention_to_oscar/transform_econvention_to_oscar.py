import json
from airflow.decorators import task
from pydantic import ValidationError
from models.activity_model import Activity
from models.convention_model import Convention


@task
def transform_econvention_to_oscar(conventions: list[dict]) -> str:
    """Transform data from ECONVENTION to OSCAR by mapping their attribute."""

    convention_list: list[Convention] = [
        Convention.model_validate(econvention) for econvention in conventions
    ]
    activity_list: list[Activity] = []
    errors = []
    for i, convention in enumerate(convention_list):
        mapping = (
            {"uid": convention.to_uid()}
            | {"acronym": convention.to_acronym()}
            | {"projectlabel": convention.to_projectlabel()}
            | {"label": convention.to_label()}
            | {"persons": convention.to_persons()}
            | {"organizations": convention.to_organizations()}
            | {"description": convention.description or ""}
            | {"type": convention.to_activity_type() or ""}
            | {"datestart": convention.to_datestart() or None}
            | {"dateend": convention.to_dateend() or None}
            | {"milestones": convention.to_milestones() or []}
        )
        try:
            activity_list.append(Activity.model_validate(mapping))
        except ValidationError as e:
            errors.append({"index": i, "errors": e.errors()})
    if len(errors) > 0:
        raise ValueError(f"Some conventions failed mapping process: {errors}")

    results = json.dumps(
        [activity.model_dump(by_alias=True) for activity in activity_list],
        sort_keys=True,
        indent=4,
    )

    return results
