def escape_characters(text: str) -> str:
    return text.replace(".", "\.").replace("(", "\(").replace(")", "\)").replace("-", "\-").replace("/", "\/").replace(
        ":", "\:").replace("+", "\+")