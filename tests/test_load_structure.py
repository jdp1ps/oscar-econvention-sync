from tests.utils.dag import (
    assert_dag_dict_equal,
)


def test_dag_loaded(econvention_to_oscar_dag):
    """
    Test dag loading
    """
    assert econvention_to_oscar_dag is not None
    assert len(econvention_to_oscar_dag.tasks) == 4


def test_dag_structure(econvention_to_oscar_dag):
    """
    Test that the DAG has the correct structure
    """
    expected_structure = {
        "receive_from_econvention": ["transform_econvention_to_oscar"],
        "transform_econvention_to_oscar": ["create_import_json_to_oscar"],
        "create_import_json_to_oscar": ["load_to_oscar"],
        "load_to_oscar": [],  # END
    }
    assert_dag_dict_equal(expected_structure, econvention_to_oscar_dag)
