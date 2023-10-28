from enum import Enum
from time import sleep

import smbus  # type: ignore


class BH1750:
    def __init__(self, address: int = 0x23, bus_number: int = 1) -> None:
        self._address = address
        self._bus = smbus.SMBus(bus_number)
        self._lux = 0

    def read_luminance(self, mode: int = 0x20) -> int:
        # Start a conversion
        self._bus.write_byte(self._address, mode)

        # Measurement time is typically 120ms, so we wait for 150ms
        sleep(0.15)

        # Read the result as 2 bytes and compute the lux value
        data = self._bus.read_i2c_block_data(self._address, 0, 2)
        self._lux = ((data[0] << 8) + data[1]) / 1.2
        return self._lux


class GPIO(Enum):
    SR04_TRIGGER = 17
    SR04_ECHO = 23
    SOUND = 24  # not used
    DHT_11 = 27


# Distance to dB mapping
distance_volume_mapping = {
    10: 56,
    15: 54,
    20: 52,
    25: 50,
    30: 48,
    35: 46,
    40: 44,
    45: 42,
    50: 40,
    55: 38,
    60: 36,
    65: 34,
    70: 32,
    75: 30,
    80: 28,
    85: 26,
    90: 24,
    95: 22,
    100: 20,
}

# Humidity + Temperature to Hz mapping
humid_temp_to_pitch_mapping = {
    18: 40,
    24: 42,
    30: 44,
    36: 46,
    42: 48,
    48: 50,
    54: 52,
    60: 54,
    66: 56,
    72: 58,
    78: 60,
    84: 62,
    90: 64,
    96: 66,
    102: 68,
    108: 70,
    114: 72,
    120: 74,
    126: 76,
}

# Lumens to seconds
light_to_duration_mapping = {
    1: 0.5,
    25: 0.6,
    50: 0.7,
    75: 0.8,
    100: 0.9,
    125: 1,
    150: 1.1,
    175: 1.2,
    200: 1.3,
    225: 1.4,
    250: 1.5,
    275: 1.6,
    300: 1.7,
    325: 1.8,
    350: 1.9,
    375: 2,
    400: 2.1,
    425: 2.2,
    450: 2.3,
}


def get_volume_from(distance: int) -> float:
    closest_value = min(distance_volume_mapping.keys(), key=lambda k: abs(k - distance))
    return distance_volume_mapping[closest_value] / 100  # Normalize to [0.0, 1.0] range for pygame


def get_pitch_from(humidity: int, temperature: int) -> int:
    closest_value = min(humid_temp_to_pitch_mapping.keys(), key=lambda k: abs(k - (humidity + temperature)))
    return humid_temp_to_pitch_mapping[closest_value]


def get_duration_from(light: int) -> float:
    closest_value = min(light_to_duration_mapping.keys(), key=lambda k: abs(k - light))
    return light_to_duration_mapping[closest_value]
