from src.pubsub import topics


def test_callable_return_value_of_get_format_topic_by_mqtt_id():
    format_topic_by_mqtt_id = topics.get_format_topic_by_mqtt_id(
        "TEST_DEVICE_TYPE_NAME"
    )
    assert callable(format_topic_by_mqtt_id)


def test_single_mqtt_id_format_topic_by_mqtt_id():
    assert (
        topics.get_format_topic_by_mqtt_id("TEST_DEVICE_TYPE_NAME")(123)
        == "/TEST_DEVICE_TYPE_NAME/123/"
    )


def test_multiple_mqtt_ids_format_topic_by_mqtt_id():
    assert topics.get_format_topic_by_mqtt_id("TEST_DEVICE_TYPE_NAME")([123, 234]) == [
        "/TEST_DEVICE_TYPE_NAME/123/",
        "/TEST_DEVICE_TYPE_NAME/234/",
    ]
