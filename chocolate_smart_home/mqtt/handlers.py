def device_data_received(client, userdata, message):
    payload = message.payload.decode()
    print(payload)
    if payload is None:
        return
