from time import sleep

import Adafruit_DHT as DHT  # type: ignore
import numpy as np  # type: ignore
import pygame  # type: ignore
from gpiozero import DistanceSensor, DistanceSensorNoEcho  # type: ignore

from .utils import BH1750, GPIO, get_duration_from, get_pitch_from, get_volume_from


def generate_tone(frequency: int, volume: float, duration: float, bpm: int) -> None:
    beat_duration = 60.0 / bpm  # Calculate the duration of a single beat in seconds
    num_beats = int(duration / beat_duration)  # Total beats within the specified duration

    # Use a dictionary to cache waveforms for unique frequency-beat_duration combinations
    waveform_cache = {}

    # Generate the waveform if it's not in the cache
    if (frequency, beat_duration) not in waveform_cache:
        samples_mono = [
            int(32767.0 * np.sin(i * 2.0 * np.pi * frequency / 44100.0)) for i in range(int(44100.0 * beat_duration))
        ]
        waveform_cache[(frequency, beat_duration)] = np.array([[s, s] for s in samples_mono], dtype=np.int16)

    samples_stereo = waveform_cache[(frequency, beat_duration)]

    sound = pygame.sndarray.make_sound(samples_stereo)
    sound.set_volume(volume)  # Set volume for the actual sound object

    for _ in range(num_beats):
        sound.play()
        pygame.time.wait(int(beat_duration * 1000))


def main() -> None:
    # Initialize pygame mixer
    pygame.mixer.init()
    # Distance sensor: HC-SR04
    distance_sensor = DistanceSensor(echo=GPIO.SR04_ECHO.value, trigger=GPIO.SR04_TRIGGER.value)
    # Light sensor: BH1750
    light_sensor = BH1750()
    sleep(5)

    def _read() -> tuple[int, int, int, int]:
        print('Reading data..')
        try:
            distance = distance_sensor.distance * 100  # Convert to centimeters
        except DistanceSensorNoEcho:
            print('DistanceSensorNoEcho encountered, using value 80 instead.')
            distance = 80
        try:
            lux = light_sensor.read_luminance()
        except OSError:
            print('Encountered error while reading lux, using value 24 instead.')
            lux = 24
        try:
            humidity, temperature = DHT.read(DHT.DHT11, GPIO.DHT_11.value)
            if humidity is None or temperature is None:
                raise ValueError('Failed to read from DHT sensor, using values 50 and 23 instead.')
        except ValueError as e:
            print(e)
            humidity = 50
            temperature = 23
        return distance, lux, humidity, temperature

    while True:
        try:
            distance, lux, humidity, temperature = _read()
            print('Distance:', distance, f' Light Level: {lux:.2f} lx', ' Humidity:', humidity, ' Temperature:', temperature)  # type: ignore
            volume = get_volume_from(distance)
            pitch = get_pitch_from(humidity, temperature)
            duration = get_duration_from(lux)
            print('Volume:', volume, ' Pitch:', pitch, 'Duration:', duration)
            generate_tone(pitch, volume, duration, 60)
            sleep(2)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
