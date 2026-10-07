from sqlalchemy import Column, Integer


class PluginModel:
    __tablename__ = "stateful_simplex_plugin"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    sensor_reading = Column(Integer)
