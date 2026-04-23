class ServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(msg: dict) -> str:
        return str(int(msg["on"]))
