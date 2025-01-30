from src.models import ModelStrFormatter


class PluginModelStrFormatter(ModelStrFormatter):
    def __str__(self):
        """Return ModelStrFormatter.__str__ result of both the OnOff
        object and its corresponding Device object."""
        return "\n".join([super().__str__(), str(self.device)])
