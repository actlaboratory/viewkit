try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8 compatibility
    from importlib_metadata import version, PackageNotFoundError


def getVersion():
    """Get the version of viewkit package from pyproject.toml

    Returns:
        str: Version string or "unknown" if package not found
    """
    try:
        return version("viewkit")
    except PackageNotFoundError:
        return "unknown"
