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
        robot = t9.RobotController()
        threading.Thread(target=robot.run, daemon=True).start()
        time.sleep(1)

        adc = ADS7830()
        controller = t3.ServoController()

        baseline = sum(adc.analogRead(1) for _ in range(20)) / 20

        current_angle = 100
        controller.set_angle(0, current_angle)

        was_en_marche = robot.en_marche

        try:
            while True:
                ecart = adc.analogRead(1) - baseline

                if ecart < -5:
                    current_angle = max(130, current_angle - 5)
                elif ecart > 5:
                    current_angle = min(60, current_angle + 5)
                else :
                    current_angle = 100

                controller.set_angle(0, current_angle)

                # Détecte l'arrêt sur obstacle
                if was_en_marche and not robot.en_marche:
                    print("Obstacle détecté, recul de 30cm")
                    robot.mc.drive_ramp(-t9.RobotController.VITESSE_MARCHE, ramp_time=2)
                    time.sleep(1.5)
                    robot.mc.drive_ramp(0.0, ramp_time=0.1)
                    controller.set_angle(0, 100)
                    time.sleep(2)
                    robot.demarrer()

                was_en_marche = robot.en_marche
                time.sleep(0.05)

        finally:
            controller.set_angle(0, 100)
            controller.deinit()

    except KeyboardInterrupt:
        pass