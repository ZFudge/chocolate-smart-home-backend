from pydantic import BaseModel


class StatefulDuplexPluginSchema(BaseModel):
    count: int
