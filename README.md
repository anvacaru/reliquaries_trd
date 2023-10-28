# Reliquaries for the Fungible

## Features

- Measure distance using the HC-SR04 distance sensor.
- Read light levels with the BH1750 light sensor.
- Detect humidity and temperature with the DHT11 sensor.
- Generate tones based on sensor readings using Pygame.

## Prerequisites

- Python 3.x
- Libraries: `gpiozero`, `Adafruit_DHT`, `numpy`, and `pygame`.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/anvacaru/reliquaries_trd.git
    ```

2. Navigate to the project directory:
    ```bash
    cd reliquaries_trd
    ```

3. Install the required packages:
    ```bash
    pip install -r gpiozero Adafruit_DHT numpy pygame
    ```

## Usage

1. Run the main script:
    ```bash
    python3 -m rfung.rfung
    ```

## License

[MIT](https://choosealicense.com/licenses/mit/)
