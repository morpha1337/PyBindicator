"""Non-secret settings: timezone, Wi-Fi retries, hardware tuning."""

config = {
    "timezone_offset": 10,
    "glowbit": {
        "brightness": 0.5,
    },
    "time": {
        "sleep_time": 5,  # seconds; used when no explicit wake time is passed
        "use_external_wake_up": True,
        "clock_sync_interval_days": 30,  # NTP again if last sync older than this
    },
    "wifi": {
        "retries": 3,
        "timeout": 800,  # ms to wait for station connect
    },
}
