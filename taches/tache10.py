import threading
import time
import smbus
import tache3 as t3
import tache9 as t9

class ADS7830(object):
    def __init__(self):
        self.cmd = 0x84
        self.bus = smbus.SMBus(1)
        self.address = 0x48

    def analogRead(self, chn):
        return self.bus.read_byte_data(
            self.address,
            self.cmd | (((chn << 2 | chn >> 1) & 0x07) << 4)
        )

if __name__ == "__main__":
    try:
        # t9 tourne 
        threading.Thread(target=t9.run, daemon=True).start()
        time.sleep(1) 

        adc = ADS7830()
        controller = t3.ServoController()

        baseline = sum(adc.analogRead(1) for _ in range(20)) / 20

        current_angle = 90
        controller.set_angle(0, current_angle)

        try:
            while True:
                ecart = adc.analogRead(1) - baseline

                if ecart < -5:
                    current_angle = max(120, current_angle - 5)
                elif ecart > 5:
                    current_angle = min(60, current_angle + 5)

                controller.set_angle(0, current_angle)
                time.sleep(0.05)

        finally:
            controller.set_angle(0, 90)
            controller.deinit()

    except KeyboardInterrupt:
        pass