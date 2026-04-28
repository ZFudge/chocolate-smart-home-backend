class ServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(msg: dict) -> str:
        if msg.get("name") != "on":
            return ""
        return str(int(msg["value"]))
