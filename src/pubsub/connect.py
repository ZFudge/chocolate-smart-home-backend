import logging
import os
import socket
import time

from paho.mqtt import MQTTException
from paho.mqtt.client import MQTTErrorCode

from src.dependencies import mqtt_client_session

logger = logging.getLogger(os.environ.get("LOGGER", "mqtt"))


def connect_to_mqtt_broker():
    mqtt_client = mqtt_client_session.get()
    host = os.environ.get("MQTT_HOST", "csm-mosquitto")
    try:
        logger.info(f"Attempting MQTT connection to {host}")
        mqtt_client.connect(host)
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
    for x in range(5):
        try:
            mqtt_error_code = mqtt_client.loop_start()
            logger.info(f"MQTT client loop start returned status: {mqtt_error_code}")
            if mqtt_error_code == MQTTErrorCode.MQTT_ERR_SUCCESS:
                break
        except MQTTException as e:
            if x == 2:
                logger.error("MQTT client loop start failed. Disconnecting... %s" % e)
                mqtt_client.disconnect()
                return
            logger.error(
                "Failed to start MQTT client loop. Reattempting loop start in 15 seconds. %s"
                % e
            )
            time.sleep(15)
