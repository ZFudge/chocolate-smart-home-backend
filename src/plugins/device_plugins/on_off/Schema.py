from pydantic import BaseModel


class OnOff(BaseModel):
    on: bool
