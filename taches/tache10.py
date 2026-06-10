import time
import smbus
import tache3 as t3

class ADS7830(object):
    def __init__(self):
        self.cmd = 0x84
        self.bus = smbus.SMBus(1)
        self.address = 0x48

    def analogRead(self, chn):
        value = self.bus.read_byte_data(
            self.address,
            self.cmd | (((chn << 2 | chn >> 1) & 0x07) << 4)
        )
        return value

if __name__ == "__main__":
    adc = ADS7830()
    controller = t3.ServoController()

    current_angle = 90
    controller.set_angle(0, current_angle)

    STEP_SIZE = 5
    MIN_ANGLE = 0
    MAX_ANGLE = 180

    try:
        while True:
            adc_value = adc.analogRead(1)
            print(f"Light Tracking Value: {adc_value} | Current Angle: {current_angle}")

            if adc_value < 125:
                current_angle -= STEP_SIZE
            elif adc_value > 150:
                current_angle += STEP_SIZE

            current_angle = max(MIN_ANGLE, min(MAX_ANGLE, current_angle))
            controller.set_angle(0, current_angle)
            time.sleep(0.05) 

    finally:
        controller.deinit()