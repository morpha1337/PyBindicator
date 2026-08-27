"""Parse Monash Council waste HTML embedded in JSON API responses."""

from __future__ import annotations

import io
from ElementTree import parse, Element
from controllers.glow_bit import RED, GREEN, YELLOW, Color
from model.bin import Bin
from controllers.wifi import WifiController
import time


def test_bin_data(bin_data: dict, wifi_controller: WifiController) -> list[Bin]:
    bins = [
        Bin("Landfill Waste", time.localtime(time.time()), RED, 0),
        Bin("Food and Garden Waste", time.localtime(time.time()), GREEN, 0),
    ]
    return bins


def get_bin_data(bin_data: dict, wifi_controller: WifiController) -> list[Bin]:
    """Fetch council schedule and return Bin objects with Monash bin colours."""
    try:
        html_result = wifi_controller.call_url_json(bin_data["bin_data_url"])["responseContent"]
        html_result = html_result.replace("\r\n", "")
    except TypeError as e:
        raise Exception("[ERROR] GOOGLE CAPTCHA!", e)

    stream = io.StringIO(html_result)
    dom = parse(stream)

    article_tags = search_tree_by_tag("article", dom.getroot())
    bins: list[Bin] = []
    for article in article_tags:
        heading = search_tree_by_tag("h3", article)[0]
        bin_type = heading.text

        date = search_tree_by_attrib("class", "next-service", article)[0]
        dateparts = date.text.strip().split(" ")[1].split("/")
        collection_date = time.struct_time([
            int(dateparts[2]),
            int(dateparts[1]),
            int(dateparts[0]),
            0,
            0,
            0,
            4,
            -1,
            -1,
        ])

        bins.append(Bin(heading.text, collection_date, get_bin_color(bin_type), 0))

    return bins


BIN_COLORS: dict[str, Color] = {
    "Landfill Waste": RED,
    "Recycling": YELLOW,
    "Food and Garden Waste": GREEN,
}


def get_bin_color(label: str) -> Color:
    """Map Monash bin type name to GlowBit RGB tuple."""
    try:
        return BIN_COLORS[label]
    except KeyError:
        raise Exception("Unknown bin type")


def print_sub_tree(node: Element, depth: int = 0) -> None:
    if node.text is not None:
        text = '"' + node.text + '"'
    else:
        text = ""
    print(" " * depth, "-", node.tag, text)
    for key, value in node.attrib.items():
        print(" " * depth, "|", key, ":", value)
    for subnode in node:
        print_sub_tree(subnode, depth + 2)


def print_node_details(node: Element) -> None:
    print("TAG: ", node.tag)
    print("InnerHTML: ", node.text)
    for k, v in node.attrib.items():
        print('{}="{}"'.format(k, v))

    print("Children: ", len(node._children))
    print("=" * 10)


def search_tree_by_tag(needle: str, stack: Element) -> list[Element]:
    arr: list[Element] = []
    if stack.tag == needle:
        arr.append(stack)
        return arr

    for subnode in stack:
        nodes = search_tree_by_tag(needle, subnode)
        if nodes:
            arr.extend(nodes)

    return arr


def search_tree_by_attrib(
    attrib_name: str, attrib_value: str, stack: Element
) -> list[Element]:
    arr: list[Element] = []
    value = stack.get(attrib_name)
    if value is not None and value == attrib_value:
        arr.append(stack)
        return arr

    for subnode in stack:
        nodes = search_tree_by_attrib(attrib_name, attrib_value, subnode)
        if nodes:
            arr.extend(nodes)

    return arr
