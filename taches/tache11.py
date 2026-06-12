import tache9 as t9
import tache6 as t6
import tache3 as t3
import threading
import time

ANGLE_CENTER = 100
ANGLE_MIN    = 60
ANGLE_MAX    = 140

if __name__ == "__main__":
    try:
        robot = t9.RobotController()
        threading.Thread(target=robot.run, daemon=True).start()
        time.sleep(1)

        linecap    = t6.LineFollower()
        controller = t3.ServoController()

        current_angle      = ANGLE_CENTER
        controller.set_angle(0, current_angle)
        was_en_marche      = robot.en_marche
        ligne_perdue_ts    = None
        angle_avant_perte  = ANGLE_CENTER

        robot.demarrer()
        nb_recule = 0
        
        while True:
            r = linecap.right.value
            m = linecap.middle.value
            l = linecap.left.value

            if   r == 0 and m == 1 and l == 0:
                current_angle = ANGLE_CENTER
                nb_recule = 0
            elif r == 1 and m == 0 and l == 0:
                current_angle += 20
                nb_recule = 0
            elif r == 0 and m == 0 and l == 1:
                current_angle -= 20
                nb_recule = 0
            elif r == 1 and m == 1 and l == 0:
                current_angle += 10
                nb_recule = 0
            elif r == 0 and m == 1 and l == 1:
                current_angle -= 10
                nb_recule = 0
            elif r == 1 and m == 1 and l == 1:
                current_angle = ANGLE_CENTER
                nb_recule = 0
            elif r == 0 and m == 0 and l == 0 and nb_recule >= 3:
                while r == 0 and m == 0 and l == 0:
                    current_angle = ANGLE_CENTER + (ANGLE_CENTER - angle_avant_perte)
                    controller.set_angle(0, current_angle)
                    robot.mc.drive_ramp(-t9.RobotController.VITESSE_MARCHE, ramp_time=0.5)
                    nb_recule = 0
            elif r == 0 and m == 0 and l == 0:
                angle_avant_perte = current_angle
                if ligne_perdue_ts is None:
                    nb_recule += 1
                    ligne_perdue_ts = time.time()

                elapsed = time.time() - ligne_perdue_ts

                # Angle inversé : symétrique par rapport au centre
                angle_recul = ANGLE_CENTER + (ANGLE_CENTER - angle_avant_perte)
                current_angle = angle_recul


                if robot.en_marche:
                    robot.arreter()
                    controller.set_angle(0, current_angle)
                    robot.mc.drive_ramp(-t9.RobotController.VITESSE_MARCHE, ramp_time=elapsed+0.4)
                    currnt_angle = angle_avant_perte  # pour préparer la reprise
                ligne_perdue_ts = None  # reset pour retenter

                robot.demarrer()

            else:
                ligne_perdue_ts = None

            # Sécurité bornes servo
            current_angle = max(ANGLE_MIN, min(ANGLE_MAX, current_angle))
            controller.set_angle(0, current_angle)

            # Reprise après obstacle
            if was_en_marche and not robot.en_marche:
                if r != 0 or m != 0 or l != 0:
                    print("Obstacle détecté — reprise dans 2s")
                    time.sleep(2)
                    robot.demarrer()

            was_en_marche = robot.en_marche
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    finally:
        controller.set_angle(0, ANGLE_CENTER)
        controller.deinit()
        robot.arreter()
        robot.desactiver_feux()
        robot.mc.destroy()