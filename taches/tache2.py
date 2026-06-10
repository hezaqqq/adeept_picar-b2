import numpy
import spidev


class LEDController:

    def __init__(self, led_count=14):
        self.led_count = led_count
        self.led_color = [0] * (self.led_count * 3)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.mode = 0

    def set_led(self, index, r, g, b, brightness=255):
        if not (0 <= index < self.led_count):
            print(f"Invalid LED index: {index} (must be 0–{self.led_count - 1})")
            return
        self.led_color[index * 3 + 1] = round(r * brightness / 255)  # red
        self.led_color[index * 3 + 0] = round(g * brightness / 255)  # green
        self.led_color[index * 3 + 2] = round(b * brightness / 255)  # blue
        self.show()

    def show(self):
        d = numpy.array(self.led_color).ravel()
        tx = numpy.zeros(len(d) * 8, dtype=numpy.uint8)
        for ibit in range(8):
            tx[7 - ibit :: 8] = ((d >> ibit) & 1) * 0x78 + 0x80
        self.spi.xfer(tx.tolist(), int(8 / 1.25e-6))

    def turn_off_all(self):
        self.led_color = [0] * (self.led_count * 3)
        self.show()


def run():
    controller = LEDController(led_count=14)
    controller.turn_off_all()
    print("Enter: <index> <r> <g> <b> [brightness]  — or 'q' to quit")

    while True:
        try:
            parts = input("> ").strip().split()

            if not parts or parts[0].lower() == "q":
                controller.turn_off_all()
                break

            index, r, g, b = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            brightness = int(parts[4]) if len(parts) >= 5 else 255
            controller.set_led(index, r, g, b, brightness)

        except (KeyboardInterrupt, SystemExit):
            controller.turn_off_all()
            break
        except (ValueError, IndexError):
            print("<index> <r> <g> <b> [brightness]")

if __name__ == "__main__":
    run()