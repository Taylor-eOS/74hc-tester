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

def test_74hc32():
    gates = [
        {'in1': 1, 'in2': 2, 'out': 3},
        {'in1': 4, 'in2': 5, 'out': 6},
        {'in1': 8, 'in2': 9, 'out': 10},
        {'in1': 11, 'in2': 12, 'out': 13}
    ]
    working_gates = 0
    contact_detected = False
    for gate in gates:
        pin_in1 = Pin(gate['in1'], Pin.OUT)
        pin_in2 = Pin(gate['in2'], Pin.OUT)
        pin_out = Pin(gate['out'], Pin.IN, Pin.PULL_DOWN)
        all_passed = True
        for val1 in (0, 1):
            for val2 in (0, 1):
                pin_in1.value(val1)
                pin_in2.value(val2)
                time.sleep_ms(5)
                out_val = pin_out.value()
                expected = 1 if val1 or val2 else 0
                if out_val != expected:
                    all_passed = False
                if out_val == 1:
                    contact_detected = True
        pin_in1.value(0)
        pin_in2.value(0)
        if all_passed:
            working_gates += 1
    return contact_detected, working_gates

def test_74hc04():
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
        pin_in.value(0)
        time.sleep_ms(5)
        low_val = pin_out.value()
        pin_in.value(1)
        time.sleep_ms(5)
        high_val = pin_out.value()
        if any(v == 1 for v in (low_val, high_val)):
            contact_detected = True
        if low_val == 1 and high_val == 0:
            working_gates += 1
        pin_in.value(0)
    return contact_detected, working_gates

def test_74hc164():
    output_pins = [3, 4, 5, 6, 10, 11, 12, 13]
    out_pins = {p: Pin(p, Pin.IN, Pin.PULL_DOWN) for p in output_pins}
    def read_outputs():
        return [out_pins[p].value() for p in output_pins]
    clr_pin = Pin(9, Pin.OUT)
    clk_pin = Pin(8, Pin.OUT)
    data_pin1 = Pin(1, Pin.OUT)
    data_pin2 = Pin(2, Pin.OUT)
    clr_pin.value(1)
    clk_pin.value(0)
    data_pin1.value(0)
    data_pin2.value(0)
    contact_detected = False
    clr_pin.value(0)
    time.sleep_ms(5)
    clr_pin.value(1)
    time.sleep_ms(5)
    low_reads = [read_outputs() for _ in range(3)]
    any_low_high = any(any(val == 1 for val in row) for row in low_reads)
    if any_low_high:
        contact_detected = True
    low_zeros = sum(1 for v in low_reads[-1] if v == 0)
    for _ in range(8):
        data_pin1.value(1)
        data_pin2.value(1)
        time.sleep_ms(1)
        clk_pin.value(1)
        time.sleep_ms(5)
        clk_pin.value(0)
        time.sleep_ms(1)
    data_pin1.value(0)
    data_pin2.value(0)
    time.sleep_ms(5)
    high_reads = [read_outputs() for _ in range(3)]
    any_high_one = any(any(val == 1 for val in row) for row in high_reads)
    if any_high_one:
        contact_detected = True
    high_ones = sum(1 for v in high_reads[-1] if v == 1)
    good_low = low_zeros >= 7
    good_high = high_ones >= 7
    working = 1 if good_low and good_high else 0
    clr_pin.value(1)
    clk_pin.value(0)
    data_pin1.value(0)
    data_pin2.value(0)
    return contact_detected, working

def main():
    set_color((32, 0, 0))
    last_contact = False
    last_working = 0
    stable_count = 0
    required_stable = 3
    while True:
        contact, working = test_74hc164()
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

