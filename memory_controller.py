"""Persist bin schedule and wake times in NVM via foamyguy_nvm_helper."""

import json
from time import struct_time
import foamyguy_nvm_helper as nvm_helper
from bin import Bin
from helpers import struct_time_to_string, string_to_struct_time


def _state_key(state: dict, new_key: str, old_key: str):
    """Read a JSON key, falling back to legacy PascalCase names."""
    if new_key in state:
        return state[new_key]
    return state.get(old_key)


def _bin_field(notif: dict, new_key: str, old_key: str):
    if new_key in notif:
        return notif[new_key]
    return notif[old_key]


class MemoryController:
    """Load and save notification state across deep-sleep restarts."""

    def __init__(self):
        self._state = None
        self.load_from_mem()

    def save_to_mem(self) -> None:
        """Write current state to NVM as JSON."""
        notifs = []
        for notif in self.notifications:
            notifs.append(notif.to_json())

        json_obj = {
            "last_wake_time": struct_time_to_string(self.last_wake_time),
            "next_wake_time": struct_time_to_string(self.last_wake_time),
            "notification_expiry_time": struct_time_to_string(self.notification_expiry_time),
            "current_notifications": notifs,
        }

        encoded_state = json.dumps(json_obj)
        print(encoded_state)
        nvm_helper.save_data(encoded_state, test_run=False, verbose=False)
        print("Saved Memory State to NVM.")

    def load_from_mem(self) -> None:
        """Load state from NVM; seed from memory.txt on first boot or corruption."""
        try:
            encoded_string = nvm_helper.read_data()
            print(encoded_string)
            self._state = json.loads(encoded_string)
            self.last_wake_time = string_to_struct_time(
                _state_key(self._state, "last_wake_time", "LastWakeTime")
            )
            self.next_wake_time = string_to_struct_time(
                _state_key(self._state, "next_wake_time", "NextWakeTime")
            )
            self.notification_expiry_time = string_to_struct_time(
                _state_key(self._state, "notification_expiry_time", "NotificationExpiryTime")
            )
            notifications_key = (
                "current_notifications"
                if "current_notifications" in self._state
                else "CurrentNotifications"
            )
            self.notifications = []
            for notif in self._state[notifications_key]:
                new_bin = Bin(
                    _bin_field(notif, "label", "Label"),
                    string_to_struct_time(
                        _bin_field(notif, "next_collection_date", "NextCollectionDate")
                    ),
                    _bin_field(notif, "color", "Color"),
                    _bin_field(notif, "collection_frequency", "CollectionFrequency"),
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

    def initialize_memory_state(self):
        """Copy defaults from memory.txt into NVM."""
        with open("memory.txt", "r") as file:
            encoded_string = file.read()
        nvm_helper.save_data(encoded_string, test_run=False, verbose=False)
        print("Initialised Memory State into NVM.")
        self.load_from_mem()

    def clear_notifications(self) -> None:
        self.notifications = []
        self.notification_expiry_time = None
        print("All Notifications Cleared from memory.")

    def add_notification(self, new_bin: Bin) -> None:
        self.notifications.append(new_bin)

    def add_notifications(self, new_bins: list) -> None:
        for new_bin in new_bins:
            self.notifications.append(new_bin)

    def update_notifications(self) -> None:
        """Advance each bin to its next future collection date."""
        for bin_inst in self.notifications:
            bin_inst.set_next_collection_date()
        print("All Notifications Next Collection Date has been recalculated.")
