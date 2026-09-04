"""Bin collection model and conversion from secrets JSON."""

from __future__ import annotations

from time import struct_time, mktime, time, localtime
from helpers import (
    struct_time_to_string,
    string_to_struct_time,
    get_today_as_epoch,
    get_days_to_seconds,
    format_struct_time,
)

Color = tuple


class Bin:
    """One waste stream with label, colour, next collection date, and frequency."""

    label: str
    next_collection_date: struct_time
    color: Color
    collection_frequency: int

    def __init__(
        self,
        label: str,
        next_collection_date: struct_time,
        color: Color,
        collection_frequency: int,
    ) -> None:
        if not isinstance(color, tuple) or len(color) != 3:
            raise TypeError("color must be an RGB tuple (r, g, b)")
        self.label = label
        self.next_collection_date = next_collection_date
        self.color = color
        self.collection_frequency = collection_frequency

    def __str__(self) -> str:
        return "Label: %s, NextCollectionDate: %s, Color: %s" % (
            self.label,
            format_struct_time(self.next_collection_date),
            self.color,
        )

    def to_json(self) -> dict:
        return {
            "label": self.label,
            "color": self.color,
            "next_collection_date": struct_time_to_string(self.next_collection_date),
            "collection_frequency": self.collection_frequency,
        }

    def has_expired(self, end_time: int = 0) -> bool:
        expiry_time = mktime(self.next_collection_date) + end_time
        return expiry_time < time()

    def is_active(self, start_time: int = 0, end_time: int = 0) -> bool:
        """True when now is within the alert window before/after collection."""
        next_collection_date_in_seconds = mktime(self.next_collection_date)
        alert_start_time = next_collection_date_in_seconds - start_time
        alert_end_time = next_collection_date_in_seconds + end_time
        now = time()
        return now > alert_start_time and now < alert_end_time

    def set_next_collection_date(self) -> None:
        """Advance next_collection_date by collection_frequency until it is today or later."""
        if self.collection_frequency <= 0:
            return

        today = get_today_as_epoch()
        next_date = mktime(self.next_collection_date)
        while next_date < today:
            next_date += self.collection_frequency
        self.next_collection_date = localtime(next_date)


def convert_json_to_bin(bin_data: list[dict]) -> list[Bin]:
    """Build Bin objects from secrets schedule, advancing dates to the next future pickup."""
    bins: list[Bin] = []
    for raw_bin in bin_data:
        start_date = string_to_struct_time(raw_bin["start_date"])
        start_date_in_seconds_since_epoch = mktime(start_date)
        frequency_in_seconds = get_days_to_seconds(int(raw_bin["frequency_in_days"]))
        today_in_seconds_since_epoch = get_today_as_epoch()
        next_collection_date = start_date_in_seconds_since_epoch

        while next_collection_date < today_in_seconds_since_epoch:
            next_collection_date += frequency_in_seconds

        next_collection_date_as_struct = localtime(next_collection_date)
        new_bin = Bin(
            raw_bin["label"],
            next_collection_date_as_struct,
            raw_bin["color"],
            frequency_in_seconds,
        )
        bins.append(new_bin)

    return bins
