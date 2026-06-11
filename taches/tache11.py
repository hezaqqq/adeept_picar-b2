import tache9 as t9
import tache6 as t6
import tache3 as t3
import threading
import time
import smbus

if __name__ == "__main__":
    try:
        robot = t9.RobotController()
        threading.Thread(target=robot.run, daemon=True).start()
        time.sleep(1)

        linecap = t6.LineFollower()
        controller = t3.ServoController()

        current_angle = 100
        controller.set_angle(0, current_angle)
        was_en_marche = robot.en_marche

        while True:
            if (linecap.right.value == 1) and (linecap.middle.value == 0) and (linecap.left.value == 0):
                current_angle -= 5
            elif (linecap.right.value == 0) and (linecap.middle.value == 0) and (linecap.left.value == 1):
                current_angle += 5
            elif (linecap.right.value == 1) and (linecap.middle.value == 1) and (linecap.left.value == 0):
                current_angle -= 2
            elif (linecap.right.value == 0) and (linecap.middle.value == 1) and (linecap.left.value == 1):
                current_angle += 2
            elif (linecap.right.value == 0) and (linecap.middle.value == 0) and (linecap.left.value == 0):
                robot.mc.drive_ramp(-t9.RobotController.VITESSE_MARCHE, ramp_time=2)
                time.sleep(1.5)

            controller.set_angle(0, current_angle)

            if was_en_marche and not robot.en_marche:
                print("Obstacle détecté")
                time.sleep(2)
                robot.demarrer()

            was_en_marche = robot.en_marche
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    finally:
        controller.set_angle(0, 100)
        controller.deinit()
        robot.arreter()
        robot.desactiver_feux()
        robot.mc.destroy()