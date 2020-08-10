"""
ipynbview CLI
"""
from pathlib import Path
from typing import List
import logging
import os

import click

import ipynbview

logger = logging.getLogger(ipynbview.__name__)


@click.command()
@click.version_option(ipynbview.__version__)
@click.argument("paths", type=click.Path(exists=True), nargs=-1)
@click.option(
    "-h",
    "--host",
    type=str,
    help="Host to listen on",
    default="127.0.0.1",
    show_default=True,
)
@click.option(
    "-p", "--port", type=int, help="Port to listen on", default=47962, show_default=True
)
@click.option("-b", "--browser", is_flag=True, help="Open homepage in browser")
@click.option("-r", "--reload", is_flag=True, help="Enable auto-reload.")
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity")
def run(
    paths: List[str], host: str, port: int, browser: bool, reload: bool, verbose: int
):
    """
    Start web application serving specified notebooks / directories containing notebooks.

    If no 'paths' are provided, defaults to current working directory."
    """
    level = logging.WARNING - (verbose * 10)
    logging.basicConfig(level=level)
    logging.debug("Set logging level to %s [%d]", logging.getLevelName(level), level)
    if not paths:
        paths = [os.getcwd()]

    uvicorn_kwargs = dict(host=host, port=port, log_level=level)

    # pylint: disable=import-outside-toplevel
    import uvicorn

    os.putenv("IPYNBVIEW_PATHS", ":".join(paths))

    if browser:
        import webbrowser

        # new=2 => open in new tab in browser window, if possible
        webbrowser.open(f"http://{host}:{port}", new=2)

    if reload:
        uvicorn.run(
            "ipynbview.app:app",
            reload=True,
            reload_dirs=[Path(__file__).parent],
            **uvicorn_kwargs,
        )
    else:
        from .app import app

        uvicorn.run(app, **uvicorn_kwargs)


main = run.main

if __name__ == "__main__":
    main(prog_name=f"python -m {ipynbview.__name__}")
