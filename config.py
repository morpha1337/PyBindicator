config = {
    'timezone_offset': 10,
    'glowbit' : {
        'brightness': 0.5
        },
    'button' : {
        'debounce': 100
        },
    'time' : {
        'sleep_time': 5, # currently this is in seconds
        'alert_begin': "12:00", # on day before collection, in 24hour time
        'alert_end': "12:00", # on collection day, in 24hour time
        'use_external_wake_up': True
        },
    'wifi' : {
        'retries': 3,
        'timeout': 800,  # How long to wait for station to connect
        }
    }
