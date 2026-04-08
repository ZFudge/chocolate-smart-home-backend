import logging
import os
import socket
import time

from paho.mqtt import MQTTException
from paho.mqtt.client import MQTTErrorCode

from src.dependencies import mqtt_client_session

# logger = logging.getLogger("mqtt")
logger = logging.getLogger(__name__)


def connect_to_mqtt_broker():
    mqtt_client = mqtt_client_session.get()
    host = os.environ.get("MQTT_HOST", "mqtt")
    port = int(os.environ.get("MQTT_PORT", 1883))
    try:
        logger.info(f"Attempting MQTT connection to {host}:{port}")
        mqtt_client.connect(host, port, 60)
        logger.info("Successfully connected to MQTT broker")
    except socket.gaierror as e:
        logger.error("Failed to connect to the MQTT broker: %s" % e)
        raise
    except MQTTException as e:
        logger.error("MQTT exception: %s" % e)
        raise
    except Exception as e:
        logger.error("Failed to connect to the MQTT broker: %s" % e)
        raise

    logger.info("Starting MQTT client loop")
    for x in range(3):
        try:
            if mqtt_client.loop_start() == MQTTErrorCode.MQTT_ERR_SUCCESS:
                break
        except MQTTException as e:
            if x == 2:
                logger.error("MQTT client loop start failed. Disconnecting... %s" % e)
                mqtt_client.disconnect()
                return
            logger.error("Failed to start MQTT client loop. Reattempting loop start in 15 seconds. %s" % e)
            time.sleep(15)
