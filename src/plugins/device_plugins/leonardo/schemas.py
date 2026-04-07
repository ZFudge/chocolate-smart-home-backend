from typing import Literal

from pydantic import BaseModel

from .commands import COMMANDS


class LeonardoMessage(BaseModel):
    command: Literal[*COMMANDS]  # type: ignore
