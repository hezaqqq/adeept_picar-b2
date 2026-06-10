#!/usr/bin/env python3
import time
import threading

import tache1 as t1
import tache2 as t2
import tache4 as t4
import tache5 as t5

# ── Constantes ───────────────────────────────────────────────
VITESSE_MARCHE   = 0.35   # throttle de marche avant (35%)
DIST_OBSTACLE_MM = 200    # seuil d'arrêt en mm (20 cm)
PERIODE_CAPTEUR  = 0.05   # lecture distance toutes les 50 ms

# ── Initialisation des modules ───────────────────────────────
leds_gpio  = t1.RobotLEDController()
leds_gpio.switchSetup()
leds_gpio.set_all_switch_off()

leds_ws    = t2.LEDController(led_count=14)
leds_ws.turn_off_all()

moteur     = t4.MotorController()
capteur    = t5.Distance()

# ── État global ──────────────────────────────────────────────
en_marche        = False   # True quand le robot avance
feux_actifs      = False   # True quand les feux de détresse clignotent
stop_feux        = threading.Event()  # signal pour arrêter le thread feux

# ── Feux de détresse ─────────────────────────────────────────
def _clignoter_feux():
    """Thread : fait clignoter toutes les LEDs jusqu'à stop_feux."""
    while not stop_feux.is_set():
        # Allumage : LEDs GPIO orange (simulé rouge+vert) + WS2812 orange
        for i in range(1, 10):
            leds_gpio.switch(i, 1)
        for i in range(14):
            leds_ws.set_led(i, 255, 80, 0)   # orange
        time.sleep(0.4)

        # Extinction
        leds_gpio.set_all_switch_off()
        leds_ws.turn_off_all()
        time.sleep(0.4)


def activer_feux():
    global feux_actifs, stop_feux
    if feux_actifs:
        return
    feux_actifs = True
    stop_feux.clear()
    threading.Thread(target=_clignoter_feux, daemon=True).start()
    print("[FEUX] Feux de détresse ON")


def desactiver_feux():
    global feux_actifs
    if not feux_actifs:
        return
    stop_feux.set()
    feux_actifs = False
    leds_gpio.set_all_switch_off()
    leds_ws.turn_off_all()
    print("[FEUX] Feux de détresse OFF")

# ── Moteur ───────────────────────────────────────────────────
def demarrer():
    global en_marche
    if en_marche:
        return
    en_marche = True
    desactiver_feux()
    t4.drive_ramp(moteur, VITESSE_MARCHE, ramp_time=1.0)
    print("[MOTEUR] Marche avant")


def arreter():
    global en_marche
    en_marche = False
    t4.drive_ramp(moteur, 0.0, ramp_time=0.5)
    print("[MOTEUR] Arrêt")

# ── Thread de surveillance du capteur ───────────────────────
def _surveiller_distance():
    """Thread : vérifie en continu la distance et arrête si obstacle."""
    while True:
        if en_marche:
            dist = capteur.checkdist()
            if dist < DIST_OBSTACLE_MM:
                print(f"[CAPTEUR] Obstacle à {dist:.0f} mm — arrêt !")
                arreter()
                activer_feux()
        time.sleep(PERIODE_CAPTEUR)

# ── Programme principal ──────────────────────────────────────
if __name__ == '__main__':
    print("=== TÂCHE 9 : Marche avant avec arrêt sur obstacle ===")
    print("  M  – démarrer la marche avant")
    print("  A  – arrêt manuel")
    print("  q  – quitter\n")

    threading.Thread(target=_surveiller_distance, daemon=True).start()

    try:
        while True:
            cmd = input("Commande > ").strip()
            if cmd == 'M':
                demarrer()
            elif cmd in ('A', 'a'):
                arreter()
                desactiver_feux()
            elif cmd == 'q':
                break
            else:
                print("  Commandes : M | A | q")

    except KeyboardInterrupt:
        print("\nFin de programme par Ctrl-C")

    finally:
        arreter()
        desactiver_feux()
        moteur.pwm_motor.deinit()
        print("Nettoyage final réalisé")