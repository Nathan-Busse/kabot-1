import time
import sys

import Adafruit_DHT
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
from time import sleep

# ---------------------------
# DHT11 Sensor Setup
# ---------------------------
SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 15  # BCM pin number for DHT11 data pin

# Morse code dictionary
morse_code_dict = {
    'Z': '--..',
    'R': '.-.',
    '6': '-....',
    'B': '-...',
    'N': '-.',
    ' ': ' '
}

# Morse code timing
dot_time = 0.2
dash_time = dot_time * 3
element_space = dot_time
char_space = dot_time * 3
word_space = dot_time * 7

def kabot_running(buzzer, element):
	print("kabot is not running")
	tone frequency = 500
	if element == '.':
		buzzer.play (Tone(tone_frequency))
		sleep(dot_time)
	elif element == '_':
		buzzer.play(Tone(tone_frequency))
		sleep(dash_time)
	buzzer.stop()
	sleep(element_space)
# ---------------------------
# Functions
# ---------------------------
def play_element(buzzer, element):
    """Play a single dot or dash on the buzzer."""
    tone_frequency = 500
    if element == '.':
        buzzer.play(Tone(tone_frequency))
        sleep(dot_time)
    elif element == '-':
        buzzer.play(Tone(tone_frequency))
        sleep(dash_time)
    buzzer.stop()
    sleep(element_space)

def play_morse_code(message, buzzer_pin):
    """Translate a string into Morse code and play it."""
    # Create buzzer only when needed
    with TonalBuzzer(buzzer_pin) as buzzer:
        print(f"Playing '{message}' in Morse code...")
        for char in message.upper():
            if char in morse_code_dict:
                code = morse_code_dict[char]
                for element in code:
                    play_element(buzzer, element)
                sleep(char_space)
            elif char == ' ':
                sleep(word_space)
            else:
                print(f"Warning: Character '{char}' not in Morse code dictionary. Skipping.")
        print("Morse code playback complete.")

# ---------------------------
# Main Loop
# ---------------------------
message_to_play = "ZR6BN"
buzzer_pin = 4

try:
    while True:
        # Read temperature and humidity
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, DHT_PIN)
        
        if humidity is not None and temperature is not None:
            print(f"Temperature: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
        else:
            print("Failed to retrieve data from DHT11 sensor")
        
        # Play Morse code (buzzer only active here)
        play_morse_code(message_to_play, buzzer_pin)
        
        # Wait 60 seconds
        print("Waiting 60 seconds...\n")
        sleep(60)

except KeyboardInterrupt:
    print("\nScript terminated by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Script finished.")



