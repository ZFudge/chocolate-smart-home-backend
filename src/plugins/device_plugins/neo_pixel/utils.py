import logging
from typing import Iterator

logger = logging.getLogger(__name__)


def received_controller_palette_value_to_hex_str_tuple(
    msg_seq: Iterator[str],
) -> tuple[int, ...]:
    """Convert iterator of 27 byte strings to named tuple of 9 hex strings."""
    try:
        complete_hex_strs = []
        current_hex = "#"
        for _ in range(27):
            byte_str = next(msg_seq)
            hex_str = f"{int(byte_str):x}".zfill(2)
            current_hex += hex_str
            if len(current_hex) == 7:
                complete_hex_strs.append(current_hex)
                current_hex = "#"
        return complete_hex_strs
    except StopIteration as e:
        logger.error(e)
        logger.error(
            "Controller palette message must be 27 comma-separated byte strings long, "
            "but iteration interrupted early: type(msg_seq)=%s, complete_hex_strs=%s, current_hex=%s"
            % (type(msg_seq), complete_hex_strs, current_hex)
        )
        logger.info("Returning default empty palette")
        return ("",) * 9
    except ValueError as e:
        logger.error(e)
        logger.info("Returning default empty palette")
        return ("",) * 9


def hex_to_byte(x: str) -> int:
    """Convert a hex string to a byte."""
    return int(x, 16)


def hex_list_to_byte_tuple(palette: list[str]) -> tuple[int, ...]:
    """Convert a list of 9 hex strings to a tuple of 27 bytes."""
    palette_bytes = []
    for hex_str in palette:
        hex_bytes = [hex_str[1 + i * 2 : 3 + i * 2] for i in range(3)]
        palette_bytes.extend(map(hex_to_byte, hex_bytes))
    return tuple(palette_bytes)


def convert_9_hex_to_27_byte_str(palette: list[str]) -> str:
    """Convert a list of 9 hex strings to a comma separated string of 27 bytes."""
    palette_bytes = hex_list_to_byte_tuple(palette)
    return ",".join(map(str, palette_bytes))


def convert_27_byte_int_to_9_hex_str(palette) -> tuple[str, ...]:
    """Convert a tuple of 27 bytes to a list of 9 hex strings."""
    hex_strings = []
    for i in range(9):
        hex_str = "#"
        for c in palette[i * 3 : i * 3 + 3]:
            hex_str += hex(int(c)).removeprefix("0x").zfill(2)
        hex_strings.append(hex_str)
    return tuple(hex_strings)
