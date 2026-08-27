"""Parse Monash Council waste HTML embedded in JSON API responses."""

from __future__ import annotations

import io
from ElementTree import parse, Element
from controllers.glow_bit import RED, GREEN, YELLOW, Color
from model.bin import Bin
from controllers.wifi import WifiController
from time import mktime, localtime, struct_time
import time


def element_text(node: Element) -> str:
    """Return stripped element text; ElementTree leaves .text None when empty."""
    if node.text is None:
        raise Exception("Missing text in <%s> element" % node.tag)
    return node.text.strip()


def parse_collection_date(date_text: str) -> struct_time:
    """Parse Monash next-service text such as 'Fri 13/1/2023'."""
    parts = date_text.split(" ")
    if len(parts) < 2:
        raise Exception("Unexpected collection date format: %s" % date_text)

    day, month, year = [int(part) for part in parts[1].split("/")]
    epoch = mktime(struct_time((year, month, day, 0, 0, 0, 0, 0, -1)))
    return localtime(epoch)


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
        headings = search_tree_by_tag("h3", article)
        if not headings:
            raise Exception("Missing <h3> in waste article")
        label = element_text(headings[0])

        date_nodes = search_tree_by_attrib("class", "next-service", article)
        if not date_nodes:
            raise Exception("Missing next-service date for %s" % label)
        collection_date = parse_collection_date(element_text(date_nodes[0]))

        bins.append(Bin(label, collection_date, get_bin_color(label), 0))

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
        raise Exception("Unknown bin type: %s" % label)


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
