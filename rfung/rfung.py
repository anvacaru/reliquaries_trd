from time import sleep

import Adafruit_DHT as DHT  # type: ignore
from gpiozero import DistanceSensor, DistanceSensorNoEcho  # type: ignore

# connect to OSC server
from pythonosc import osc_bundle_builder  # type: ignore
from pythonosc import osc_message_builder  # type: ignore
from pythonosc import udp_client  # type: ignore

from .utils import BH1750, GPIO, get_duration_from, get_pitch_from, get_volume_from

OSC_ADDR = '127.0.0.1'
OSC_PORT = 57120

osc_client = udp_client.SimpleUDPClient(OSC_ADDR, OSC_PORT)


def main() -> None:
    # Distance sensor: HC-SR04
    distance_sensor = DistanceSensor(echo=GPIO.SR04_ECHO.value, trigger=GPIO.SR04_TRIGGER.value)
    # Light sensor: BH1750
    light_sensor = BH1750()
    # Initialize with default values
    previous_distance = 80
    previous_lux = 24
    previous_humidity = 50
    previous_temperature = 23
    sleep(5)

    def _read() -> tuple[int, int, int, int]:
        nonlocal previous_distance, previous_lux, previous_humidity, previous_temperature
        try:
            distance = distance_sensor.distance * 100  # Convert to centimeters
        except DistanceSensorNoEcho:
            distance = previous_distance
        try:
            lux = light_sensor.read_luminance()
        except OSError:
            lux = previous_lux
        try:
            humidity, temperature = DHT.read(DHT.DHT11, GPIO.DHT_11.value)
            if humidity is None or temperature is None:
                raise ValueError()
        except ValueError:
            humidity = previous_humidity
            temperature = previous_temperature

        previous_distance = distance
        previous_lux = lux
        previous_humidity = humidity
        previous_temperature = temperature

        return distance, lux, humidity, temperature

    while True:
        try:
            distance, lux, humidity, temperature = _read()

            volume = get_volume_from(distance)
            pitch = get_pitch_from(humidity, temperature)
            duration = get_duration_from(lux)

            # send data over OSC to Supercollider
            bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
            msg = osc_message_builder.OscMessageBuilder(address='/sense')
            msg.add_arg(distance)
            msg.add_arg(lux)
            msg.add_arg(humidity)
            msg.add_arg(temperature)
            msg.add_arg(volume)
            msg.add_arg(pitch)
            msg.add_arg(duration)
            bundle.add_content(msg.build())
            osc_client.send(bundle.build())

            sleep(0.1)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
