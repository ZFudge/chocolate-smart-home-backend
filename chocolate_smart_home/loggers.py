import logging

LOG_PATH = "/tmp/chocolate_smart_home"

format_str = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s"
log_formatter = logging.Formatter(format_str)

root_logger = logging.getLogger()

root_file_handler = logging.FileHandler(f"{LOG_PATH}.log")
root_file_handler.setFormatter(log_formatter)
root_logger.addHandler(root_file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

root_logger.addHandler(console_handler)

mqtt_logger = logging.getLogger("scheduler")

mqtt_file_handler = logging.FileHandler(f"{LOG_PATH}.mqtt.log")
mqtt_file_handler.setFormatter(log_formatter)
mqtt_logger.addHandler(mqtt_file_handler)
