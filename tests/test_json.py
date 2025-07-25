import json
import os


def test_json_reading(path="demo_data/test_data_oscar.json"):
    with open(path, "r") as f:
        data = json.load(f)
    assert isinstance(data, list)
    return data


def test_json_writing(
    input_path="demo_data/test_data_oscar.json",
    output_path="demo_data/test_output.json",
):
    data = test_json_reading(input_path)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    with open(output_path, "r") as f:
        data_written = json.load(f)

    assert data == data_written


# def test_json_convert_eConvention_To_Oscar(input_path='demo_data/test_data_econvention.json', output_path='demo_data/test_data_oscar.json'):

if __name__ == "__main__":
    test_json_reading()
    test_json_writing()
