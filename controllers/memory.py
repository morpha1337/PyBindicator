"""Persist bin schedule and wake times in NVM via foamyguy_nvm_helper."""

from __future__ import annotations

import json
from time import struct_time

import foamyguy_nvm_helper as nvm_helper
from model.bin import Bin
from helpers import struct_time_to_string, string_to_struct_time

try:
    from typing import Optional
except ImportError:
    pass


class MemoryController:
    """Load and save notification state across deep-sleep restarts."""

    _state: Optional[dict]
    last_wake_time: Optional[struct_time]
    next_wake_time: Optional[struct_time]
    last_clock_sync: Optional[struct_time]
    notification_expiry_time: Optional[struct_time]
    notifications: list[Bin]

    def __init__(self) -> None:
        self._state = None
        self.last_wake_time = None
        self.next_wake_time = None
        self.last_clock_sync = None
        self.notification_expiry_time = None
        self.notifications = []
        self.load_from_mem()

    def save_to_mem(self) -> None:
        """Write current state to NVM as JSON."""
        notifs = []
        for notif in self.notifications:
            notifs.append(notif.to_json())

        json_obj = {
            "last_wake_time": struct_time_to_string(self.last_wake_time),
            "next_wake_time": struct_time_to_string(self.next_wake_time),
            "last_clock_sync": struct_time_to_string(self.last_clock_sync),
            "notification_expiry_time": struct_time_to_string(self.notification_expiry_time),
            "current_notifications": notifs,
        }

        encoded_state = json.dumps(json_obj)
        print("Saving Memory State to NVM:")
        print(encoded_state)
        nvm_helper.save_data(encoded_state, test_run=False, verbose=False)
        print("================")

    def load_from_mem(self) -> None:
        """Load state from NVM; seed from memory.txt on first boot or corruption."""
        try:
            encoded_string = nvm_helper.read_data()
            print("===============")
            print("Loading Memory State from NVM:")
            print(encoded_string)
            self._state = json.loads(encoded_string)
            self.last_wake_time = string_to_struct_time(self._state["last_wake_time"])
            self.next_wake_time = string_to_struct_time(self._state["next_wake_time"])
            # Missing key = pre-migration NVM; treat as never synced.
            self.last_clock_sync = string_to_struct_time(self._state.get("last_clock_sync"))
            self.notification_expiry_time = string_to_struct_time(
                self._state["notification_expiry_time"]
            )
            self.notifications = []
            for notif in self._state["current_notifications"]:
                new_bin = Bin(
                    notif["label"],
                    string_to_struct_time(notif["next_collection_date"]),
                    tuple(notif["color"]),
                    notif["collection_frequency"],
                )
                self.notifications.append(new_bin)

            print("Loaded Memory State from NVM.")
        except EOFError:
            print("[EOFError] memory state error; re-loaded default memory state")
            self.initialize_memory_state()
        except KeyError:
            print("[KeyError] memory state error; re-loaded default memory state")
            self.initialize_memory_state()
        except ValueError:
            print("[ValueError] memory state error; re-loaded default memory state")
            self.initialize_memory_state()

    def initialize_memory_state(self) -> None:
        """Copy defaults from memory.txt into NVM."""
        with open("memory.txt", "r") as file:
            encoded_string = file.read()
        nvm_helper.save_data(encoded_string, test_run=False, verbose=False)
        print("Initialized Memory State into NVM.")
        self.load_from_mem()

    def clear_notifications(self) -> None:
        self.notifications = []
        self.notification_expiry_time = None
        print("All Notifications Cleared from memory.")

    def add_notification(self, new_bin: Bin) -> None:
        self.notifications.append(new_bin)

    def add_notifications(self, new_bins: list[Bin]) -> None:
        for new_bin in new_bins:
            self.notifications.append(new_bin)

    def update_notifications(self) -> None:
        """Advance each bin to its next future collection date."""
        for bin_inst in self.notifications:
            bin_inst.set_next_collection_date()
        print("All notification next collection dates have been recalculated.")
