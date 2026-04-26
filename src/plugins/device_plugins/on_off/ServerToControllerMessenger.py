class ServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(msg: dict) -> str:
        if "on" not in msg:
            return ""
        return str(int(msg["on"]))
