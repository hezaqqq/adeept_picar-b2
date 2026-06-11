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

        current_angle   = ANGLE_CENTER
        controller.set_angle(0, current_angle)
        was_en_marche   = robot.en_marche
        ligne_perdue_ts = None   # timestamp du moment où la ligne a été perdue

        robot.demarrer()

        while True:
            r = linecap.right.value
            m = linecap.middle.value
            l = linecap.left.value

            # ── Suivi de ligne ────────────────────────────────────────
            if   r == 0 and m == 1 and l == 0:
                current_angle = ANGLE_CENTER          # ligne droite
            elif r == 1 and m == 0 and l == 0:
                current_angle += 5                    # déviation droite → corriger droite
            elif r == 0 and m == 0 and l == 1:
                current_angle -= 5                    # déviation gauche → corriger gauche
            elif r == 1 and m == 1 and l == 0:
                current_angle += 2                    # légère droite
            elif r == 0 and m == 1 and l == 1:
                current_angle -= 2                    # légère gauche
            elif r == 1 and m == 1 and l == 1:
                current_angle = ANGLE_CENTER          # intersection → tout droit

            elif r == 0 and m == 0 and l == 0:
                # Ligne perdue
                if ligne_perdue_ts is None:
                    ligne_perdue_ts = time.time()

                elapsed = time.time() - ligne_perdue_ts

                if elapsed < 1.0:
                    # Phase 1 : on continue tout droit brièvement
                    pass
                elif elapsed < 3.0:
                    # Phase 2 : on recule doucement pour retrouver la ligne
                    if robot.en_marche:
                        robot.arreter()
                        robot.mc.drive_ramp(-t9.RobotController.VITESSE_MARCHE, ramp_time=0.3)
                    current_angle = ANGLE_CENTER
                else:
                    # Phase 3 : ligne toujours pas trouvée → stop total
                    robot.arreter()
            else:
                ligne_perdue_ts = None  # ligne retrouvée, reset

            # Sécurité bornes servo
            current_angle = max(ANGLE_MIN, min(ANGLE_MAX, current_angle))
            controller.set_angle(0, current_angle)

            # ── Reprise après obstacle ────────────────────────────────
            if was_en_marche and not robot.en_marche:
                # Vérifie que c'est bien un obstacle (pas une perte de ligne)
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