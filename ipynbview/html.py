from dataclasses import dataclass
from functools import singledispatch
from html import escape
from typing import Callable, Collection, Optional, Union


@dataclass(frozen=True)
class Attr:
    name: str
    value: Optional[str] = None


@dataclass(frozen=True)
class Element:
    name: str
    attributes: Collection[Attr] = ()
    children: Collection[Union["Element", str]] = ()


def el(name: str, *children, **attributes) -> Element:
    attributes = [
        Attr(name, value) if value is not True else Attr(name)
        for name, value in attributes.items()
    ]
    return Element(name, attributes, children)


def h(name: str) -> Callable[..., Element]:
    def _el(*children, **attributes) -> Element:
        return el(name, *children, **attributes)

    return _el


@singledispatch
def render_html(node) -> str:
    raise NotImplementedError(node)


@render_html.register
def render_html_str(string: str) -> str:
    return string


@render_html.register
def render_html_attr(attr: Attr) -> str:
    if attr.value is not None:
        return f'{escape(attr.name)}="{escape(attr.value)}"'
    return f"{escape(attr.name)}"


@render_html.register
def render_html_element(element: Element) -> str:
    start_tag_parts = (escape(element.name), *map(render_html, element.attributes))
    return "".join(
        [
            f"<{' '.join(start_tag_parts)}>",
            *map(render_html, element.children),
            f"</{escape(element.name)}>",
        ]
    )
