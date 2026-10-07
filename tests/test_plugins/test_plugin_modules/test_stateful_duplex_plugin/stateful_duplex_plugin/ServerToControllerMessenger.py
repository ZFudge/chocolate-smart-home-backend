class ServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(msg: dict) -> str:
        return f"count={msg.values()}"
