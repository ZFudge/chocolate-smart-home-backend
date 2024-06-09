from chocolate_smart_home.schemas.utils import to_schema
from .model import OnOff
from .schemas import OnOffDevice


def to_on_off_schema(on_off: OnOff) -> OnOffDevice:
    return OnOffDevice(
        id=on_off.id,
        on=on_off.on,
        device=to_schema(on_off.device),
    )
