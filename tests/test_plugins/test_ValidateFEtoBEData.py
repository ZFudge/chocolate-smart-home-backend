import pytest

from src.plugins.bases.ValidateFEtoBEData import ValidateFEtoBEData


def test_ValidateFEtoBEData_validate_msg_data_raises_ValueError_when_passed_empty_dict():
    with pytest.raises(
        ValueError,
        match="data must contain device_type_name, mqtt_id, name, and value. Missing keys: \\['device_type_name', 'mqtt_id', 'value'\\]",
    ):
        ValidateFEtoBEData().validate_msg_data({"name": "test_name"})
    with pytest.raises(
        ValueError,
        match="data must contain device_type_name, mqtt_id, name, and value. Missing keys: \\['device_type_name', 'mqtt_id'\\]",
    ):
        ValidateFEtoBEData().validate_msg_data(
            {"name": "test_name", "value": "test_value"}
        )
    with pytest.raises(
        ValueError,
        match="data must contain device_type_name, mqtt_id, name, and value. Missing keys: \\['device_type_name'\\]",
    ):
        ValidateFEtoBEData().validate_msg_data(
            {"name": "test_name", "value": "test_value", "mqtt_id": 123}
        )
    with pytest.raises(
        ValueError,
        match="data must contain device_type_name, mqtt_id, name, and value. Missing keys: \\['mqtt_id'\\]",
    ):
        ValidateFEtoBEData().validate_msg_data(
            {
                "name": "test_name",
                "value": "test_value",
                "device_type_name": "test_device_type_name",
            }
        )
    with pytest.raises(
        ValueError,
        match="data must contain device_type_name, mqtt_id, name, and value. Missing keys: \\['device_type_name', 'mqtt_id', 'name', 'value'\\]",
    ):
        ValidateFEtoBEData().validate_msg_data({})
