"""Non-secret settings: timezone, alert window, Wi-Fi retries, hardware tuning."""

config = {
    "timezone_offset": 10,
    "glowbit": {
        "brightness": 0.5,
    },
    "button": {
        "debounce": 100,
    },
    "time": {
        "sleep_time": 5,  # seconds; used when no explicit wake time is passed
        "alert_begin": "12:00",  # on day before collection, 24 h clock
        "alert_end": "12:00",  # on collection day, 24 h clock
        "use_external_wake_up": True,
    },
    "wifi": {
        "retries": 3,
        "timeout": 800,  # ms to wait for station connect
    },
}
