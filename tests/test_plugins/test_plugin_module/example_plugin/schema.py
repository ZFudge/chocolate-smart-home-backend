from pydantic import BaseModel


class ExamplePluginSchema(BaseModel):
    count: int
