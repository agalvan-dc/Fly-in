from .factory import Factory, Linkers


def parser(filepath: str | None = None) -> None:
    """
    Parse a raw text map configuration and construct network graph files.

    Args:
        filepath: Optional path to the text map file.
    """
    Factory(filepath)
    Linkers()
