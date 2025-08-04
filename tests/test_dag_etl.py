from tests.utils.dag import assert_dag_dict_equal

def test_dag_loaded(dagbag):
    """
    Test dag loading
    :param dagbag:
    :return:
    """
    dag = dagbag.get_dag(dag_id="dag_etl")
    assert dagbag.import_errors == {}
    assert dag is not None
    assert len(dag.tasks) == 4


def test_dag_structure(dagbag):
    """
        Test that the DAG has the correct structure
        :param dagbag: dagbag fixture
        :return: None
    """
    dag = dagbag.get_dag(dag_id="dag_etl")
    expected_structure = {
        "extract_from_econvention": ["transform_from_econvention_to_oscar"],
        "transform_from_econvention_to_oscar": ["load"],
        "load": ["load_to_oscar"],
        "load_to_oscar": [], #END
    }
    assert_dag_dict_equal(expected_structure, dag)
