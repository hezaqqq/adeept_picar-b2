import tache9 as t9
import tache6 as t6
import tache3 as t3
import tache1 as t1
import threading
import time

ANGLE_CENTER = 100
ANGLE_MIN    = 60
ANGLE_MAX    = 140

LEDS_DROITE    = [7, 9]       # 17, 19
LEDS_GAUCHE    = [4, 6]       # 14, 16
LEDS_TOUT_DROIT = [4, 5, 6, 7, 8, 9]  # 14 à 19

def set_direction_leds(led_ctrl, direction):
    """direction : 'droite', 'gauche', 'tout_droit', ou 'off'"""
    # Éteindre toutes les LEDs 4 à 9
    for i in range(4, 10):
        led_ctrl.switch(i, 0)

    if direction == "droite":
        for i in LEDS_DROITE:
            led_ctrl.switch(i, 1)
    elif direction == "gauche":
        for i in LEDS_GAUCHE:
            led_ctrl.switch(i, 1)
    elif direction == "tout_droit":
        for i in LEDS_TOUT_DROIT:
            led_ctrl.switch(i, 1)

if __name__ == "__main__":
    try:
        robot = t9.RobotController()
        threading.Thread(target=robot.run, daemon=True).start()
        time.sleep(1)

        linecap    = t6.LineFollower()
        controller = t3.ServoController()

        # Init LEDs
        led_ctrl = t1.RobotLEDController()
        led_ctrl.switchSetup()
        led_ctrl.set_all_switch_off()

        current_angle      = ANGLE_CENTER
        controller.set_angle(0, current_angle)
        was_en_marche      = robot.en_marche
        ligne_perdue_ts    = None
        angle_avant_perte  = ANGLE_CENTER
        last_direction     = None  # Pour éviter les appels répétés inutiles

        previous_r = previous_m = previous_l = 1

        robot.demarrer()
        
        while True:
            r = linecap.right.value
            m = linecap.middle.value
            l = linecap.left.value

            direction = None  # direction déterminée à chaque itération

            if r == 0 and m == 1 and l == 0:
                current_angle = ANGLE_CENTER
                t9.RobotController.VITESSE_MARCHE = 0.3
                direction = "tout_droit"

            elif r == 1 and m == 0 and l == 0:
                current_angle += 20
                t9.RobotController.VITESSE_MARCHE = 0.25
                direction = "droite"

            elif r == 0 and m == 0 and l == 1:
                current_angle -= 20
                t9.RobotController.VITESSE_MARCHE = 0.25
                direction = "gauche"

            elif r == 1 and m == 1 and l == 0:
                current_angle += 10
                t9.RobotController.VITESSE_MARCHE = 0.3
                direction = "droite"

            elif r == 0 and m == 1 and l == 1:
                current_angle -= 10
                t9.RobotController.VITESSE_MARCHE = 0.3
                direction = "gauche"

            elif r == 1 and m == 1 and l == 1:
                current_angle = ANGLE_CENTER
                direction = "tout_droit"

            elif r == 0 and m == 0 and l == 0:
                direction = "off"
                if (previous_r == 0 and previous_m == 1 and previous_l == 0) or (previous_r == 1 and previous_m == 1 and previous_l == 1):
                    robot.mc.drive_ramp(t9.RobotController.VITESSE_MARCHE, ramp_time=0.7)
                else:    
                    angle_avant_perte = current_angle
                    if ligne_perdue_ts is None:
                        ligne_perdue_ts = time.time()

                    elapsed = time.time() - ligne_perdue_ts

                    angle_recul = ANGLE_CENTER + (ANGLE_CENTER - angle_avant_perte)
                    current_angle = angle_recul

                    if robot.en_marche:
                        robot.arreter()
                        controller.set_angle(0, current_angle)
                        robot.mc.drive_ramp(-t9.RobotController.VITESSE_MARCHE, ramp_time=elapsed+0.5)
                    ligne_perdue_ts = None

                    current_angle = angle_avant_perte
                    controller.set_angle(0, current_angle)
                    robot.demarrer()
            
            else:
                direction = "off"
                ligne_perdue_ts = None

            # Mise à jour LEDs seulement si la direction change
            if direction is not None and direction != last_direction:
                set_direction_leds(led_ctrl, direction)
                last_direction = direction

            previous_r = previous_m = previous_l = r, m, l
            
            current_angle = max(ANGLE_MIN, min(ANGLE_MAX, current_angle))
            controller.set_angle(0, current_angle)

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
        led_ctrl.set_all_switch_off()