from pathlib import Path
from typing import Collection, Iterable, Iterator
import logging
import os

import fastapi
from fastapi.responses import HTMLResponse

from nbconvert.exporters.html import HTMLExporter

from .html import Element, h, render_html

logger = logging.getLogger(__name__)

app = fastapi.FastAPI()

IGNORE_NAMES = {
    ".DS_Store",
    ".ipynb_checkpoints",
}


@app.get("/")
async def listing():
    tops: Collection[Path] = [
        Path(path) for path in os.getenv("IPYNBVIEW_PATHS", "").split(":") if path
    ]
    logger.info("Listing tops: %r", tops)

    def paths_to_elements(*paths: Iterable[Path]) -> Iterator[Element]:
        for path in paths:
            if path.name not in IGNORE_NAMES:
                if path.is_dir():
                    children = sorted(path.iterdir())
                    yield h("li")(
                        path.name, "/", h("ul")(*paths_to_elements(*children))
                    )
                # otherwise, is file...
                elif path.suffix == ".ipynb":
                    yield h("li")(h("a")(path.name, href=str(path)))
                else:
                    yield h("li")(path.name)

    # full layout
    document = h("main")(h("h1")("Paths"), h("ul")(*paths_to_elements(*tops)))
    html_content = render_html(document)
    return HTMLResponse(content=html_content)


@app.get("{filepath:path}.ipynb")
async def ipynbhtml(filepath: str) -> str:
    filepath = f"{filepath}.ipynb"
    html_exporter = HTMLExporter()
    html_content, resources = html_exporter.from_filename(filepath)
    # resources has keys like:
    #   metadata, output_extension, inlining, raw_mimetypes, global_content_filter
    return HTMLResponse(content=html_content)
