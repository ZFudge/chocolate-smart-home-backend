def snakecase_to_pascalcase(string: str) -> str:
    return "".join(map(str.title, string.split("_")))
