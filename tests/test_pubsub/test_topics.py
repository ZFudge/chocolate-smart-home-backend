from src.pubsub import topics


def test_pubsub_get_format_topic_by_mqtt_id_return_value_is_callable():
    format_topic_by_mqtt_id = topics.get_format_topic_by_mqtt_id_using_device_type_name(
        "TEST_DEVICE_TYPE_NAME"
    )
    assert callable(format_topic_by_mqtt_id)


def test_pubsub_format_topic_by_mqtt_id_with_single_mqtt_id():
    assert (
        topics.get_format_topic_by_mqtt_id_using_device_type_name(
            "TEST_DEVICE_TYPE_NAME"
        )(123)
        == "/TEST_DEVICE_TYPE_NAME/123/"
    )


def test_pubsub_format_topic_by_mqtt_id_with_multiple_mqtt_ids():
    assert topics.get_format_topic_by_mqtt_id_using_device_type_name(
        "TEST_DEVICE_TYPE_NAME"
    )([123, 234]) == [
        "/TEST_DEVICE_TYPE_NAME/123/",
        "/TEST_DEVICE_TYPE_NAME/234/",
    ]
