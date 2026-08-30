from .factory import Factory, Linkers

def parser(filepath: str | None = None) -> None:
    Factory(filepath)
    Linkers()

