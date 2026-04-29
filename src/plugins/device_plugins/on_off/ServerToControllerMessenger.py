class ServerToControllerMessenger:
    def compose_controller_msg(self, msg_data: dict) -> str:
        super().compose_controller_msg(msg_data)
        if msg_data.get("name") != "on":
            return ""
        return str(int(msg_data["value"]))
