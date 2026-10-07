from pydantic import BaseModel


class StatefulSimplexPluginSchema(BaseModel):
    sensor_reading: int
