from machine import Pin
from neopixel import NeoPixel
import time

LED_PIN = 23
LED_COUNT = 1

np = NeoPixel(Pin(LED_PIN), LED_COUNT)

def set_color(col):
    np[0] = col
    np.write()

def test_74hc14():
    gates = [
        {'in': 1, 'out': 2},
        {'in': 3, 'out': 4},
        {'in': 5, 'out': 6},
        {'in': 9, 'out': 8},
        {'in': 11, 'out': 10},
        {'in': 13, 'out': 12}
    ]
    working_gates = 0
    contact_detected = False
    for gate in gates:
        pin_in = Pin(gate['in'], Pin.OUT)
        pin_out = Pin(gate['out'], Pin.IN, Pin.PULL_DOWN)
        results_low = []
        results_high = []
        for _ in range(3):
            pin_in.value(0)
            time.sleep_ms(5)
            results_low.append(pin_out.value())
            pin_in.value(1)
            time.sleep_ms(5)
            results_high.append(pin_out.value())
        if any(r == 1 for r in results_low + results_high):
            contact_detected = True
        if all(r == 1 for r in results_low) and all(r == 0 for r in results_high):
            working_gates += 1
        pin_in.value(0)
    return contact_detected, working_gates

def main():
    set_color((32, 0, 0))
    last_contact = False
    last_working = 0
    stable_count = 0
    required_stable = 3
    while True:
        contact, working = test_74hc14()
        if contact == last_contact and working == last_working:
            stable_count += 1
        else:
            stable_count = 0
            last_contact = contact
            last_working = working
        if stable_count >= required_stable:
            if working >= 1:
                set_color((0, 64, 0))
            elif contact:
                set_color((64, 32, 0))
            else:
                set_color((32, 0, 0))
        time.sleep_ms(100)

if __name__ == "__main__":
    main()
