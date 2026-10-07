import os

BACKEND_STREAM_NAME = os.getenv("BACKEND_STREAM_NAME")
WEBSOCKETS_STREAM_NAME = os.getenv("WEBSOCKETS_STREAM_NAME")

not_set = []
if not BACKEND_STREAM_NAME:
    not_set.append("BACKEND_STREAM_NAME")
if not WEBSOCKETS_STREAM_NAME:
    not_set.append("WEBSOCKETS_STREAM_NAME")
if not_set:
    raise ValueError(f"{', '.join(not_set)} must be set")
