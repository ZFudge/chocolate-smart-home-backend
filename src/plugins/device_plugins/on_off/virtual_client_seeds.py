# seed data for virtual clients, to simulate On/Off Virtual Client controllers during development

seeds = [
    {
        "name": "On/Off Virtual Client 0",
        "on": False,
    },
    {
        "name": "On/Off Virtual Client 1",
        "on": True,
    },
    {
        "name": "On/Off Virtual Client 2",
        "on": False,
    },
    {
        "name": "On/Off Virtual Client 3",
        "on": True,
    },
    {
        "name": "On/Off Virtual Client 4",
        "on": True,
    },
    {
        "name": "On/Off Virtual Client 5",
        "on": False,
    },
    {
        "name": "On/Off Virtual Client 6",
        "on": True,
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
