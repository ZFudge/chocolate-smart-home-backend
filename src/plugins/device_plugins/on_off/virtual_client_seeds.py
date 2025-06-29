# seed data for virtual clients, to simulate on/off controllers during development

seeds = [
    {
        "name": "On/Off 1",
        "on": True,
    },
    {
        "name": "On/Off 2",
        "on": False,
    },
    {
        "name": "On/Off 3",
        "on": True,
    },
    {
        "name": "On/Off 4",
        "on": True,
    },
    {
        "name": "On/Off 5",
        "on": False,
    },
    {
        "name": "On/Off 6",
        "on": True,
    },
    {
        "name": "On/Off 7",
        "on": True,
    },
    {
        "name": "On/Off 8",
        "on": False,
    },
    {
        "name": "On/Off 9",
        "on": True,
    },
    {
        "name": "On/Off 10",
        "on": False,
    },
]

def translate_vc_dict_to_mqtt_msg(seed: dict) -> str:
    """Mocks the controller state expected by the CSM server"""
    # cast bool to int
    on = int(seed["on"])

    msg_values = [
        # Add configs
        seed["mqtt_id"],
        seed["device_type_name"],
        seed["name"],
        # Add state
        on,
    ]

    msg_values = map(str, msg_values)

    return ",".join(msg_values)
