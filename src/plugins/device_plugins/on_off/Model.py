from sqlalchemy import Boolean, Column, Integer


class PluginModel:
    __tablename__ = "on_off"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    on = Column(Boolean, nullable=True)
