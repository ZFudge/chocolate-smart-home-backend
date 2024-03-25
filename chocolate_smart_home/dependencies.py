from chocolate_smart_home import models
from chocolate_smart_home.database import SessionLocal, engine
from chocolate_smart_home.mqtt.client import MQTTClient

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mqtt_client():
    mqtt_client = MQTTClient("127.0.0.1")
    mqtt_client.connect()

    try:
        yield mqtt_client
    finally:
        mqtt_client.disconnect()
