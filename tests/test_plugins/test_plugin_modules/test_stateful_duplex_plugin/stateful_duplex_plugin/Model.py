from sqlalchemy import Column, Integer, String


class PluginModel:
    __tablename__ = "stateful_duplex_plugin"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    count = Column(Integer)
    example_server_side_value = Column(String)
