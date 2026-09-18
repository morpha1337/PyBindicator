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
    """One waste stream with label, colour, alert window, and frequency."""

    label: str
    next_collection_date: struct_time
    next_collection_end_date: struct_time
    color: Color
    collection_frequency: int

    def __init__(
        self,
        label: str,
        next_collection_date: struct_time,
        color: Color,
        collection_frequency: int,
        next_collection_end_date: struct_time,
    ) -> None:
        if not isinstance(color, tuple) or len(color) != 3:
            raise TypeError("color must be an RGB tuple (r, g, b)")
        self.label = label
        self.next_collection_date = next_collection_date
        self.next_collection_end_date = next_collection_end_date
        self.color = color
        self.collection_frequency = collection_frequency

    def __str__(self) -> str:
        return "Label: %s, Start: %s, End: %s, Color: %s" % (
            self.label,
            format_struct_time(self.next_collection_date),
            format_struct_time(self.next_collection_end_date),
            self.color,
        )

    def to_json(self) -> dict:
        return {
            "label": self.label,
            "color": self.color,
            "next_collection_date": struct_time_to_string(self.next_collection_date),
            "next_collection_end_date": struct_time_to_string(self.next_collection_end_date),
            "collection_frequency": self.collection_frequency,
        }

    def has_expired(self) -> bool:
        return mktime(self.next_collection_end_date) < time()

    def is_active(self) -> bool:
        """True when now is within this bin's alert window [start, end)."""
        now = time()
        return (
            now >= mktime(self.next_collection_date)
            and now < mktime(self.next_collection_end_date)
        )

    def set_next_collection_date(self) -> None:
        """Advance start and end by collection_frequency until start is today or later."""
        if self.collection_frequency <= 0:
            return

        today = get_today_as_epoch()
        next_date = mktime(self.next_collection_date)
        end_date = mktime(self.next_collection_end_date)
        while next_date < today:
            next_date += self.collection_frequency
            end_date += self.collection_frequency
        self.next_collection_date = localtime(next_date)
        self.next_collection_end_date = localtime(end_date)


def convert_json_to_bin(bin_data: list[dict]) -> list[Bin]:
    """Build Bin objects from secrets schedule, advancing dates to the next future pickup."""
    bins: list[Bin] = []
    for raw_bin in bin_data:
        start_date = string_to_struct_time(raw_bin["start_date"])
        end_date = string_to_struct_time(raw_bin["end_date"])
        start_epoch = mktime(start_date)
        end_epoch = mktime(end_date)
        frequency_in_seconds = get_days_to_seconds(int(raw_bin["frequency_in_days"]))
        today_in_seconds_since_epoch = get_today_as_epoch()

        while start_epoch < today_in_seconds_since_epoch:
            start_epoch += frequency_in_seconds
            end_epoch += frequency_in_seconds

        bins.append(
            Bin(
                raw_bin["label"],
                localtime(start_epoch),
                raw_bin["color"],
                frequency_in_seconds,
                localtime(end_epoch),
            )
        )

    return bins
