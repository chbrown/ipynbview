__version__ = None

try:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("ipynbview").version
except Exception:
    pass
