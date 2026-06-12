#!/usr/bin/env python3
import time
import threading

import tache1 as t1
import tache2 as t2
import tache4 as t4
import tache5 as t5

class RobotController:

    VITESSE_MARCHE   = 0.4
    DIST_OBSTACLE_MM = 200.0
    PERIODE_CAPTEUR  = 0.05

    def __init__(self):
        self.leds_gpio = t1.RobotLEDController()
        self.leds_gpio.switchSetup()
        self.leds_gpio.set_all_switch_off()

        self.leds_ws = t2.LEDController(led_count=14)
        self.leds_ws.turn_off_all()

        self.mc      = t4.MotorController()
        self.capteur = t5.Distance()

        self.en_marche   = False
        self.feux_actifs = False
        self.stop_feux   = threading.Event()

    # ── Feux ──────────────────────────────────────────────────

    def _clignoter_feux(self):
        while not self.stop_feux.is_set():
            for i in range(1, 10):
                self.leds_gpio.switch(i, 1)
            for i in range(14):
                self.leds_ws.set_led(i, 255, 80, 0)
            time.sleep(0.4)
            self.leds_gpio.set_all_switch_off()
            self.leds_ws.turn_off_all()
            time.sleep(0.4)

    def activer_feux(self):
        if self.feux_actifs:
            return
        self.feux_actifs = True
        self.stop_feux.clear()
        threading.Thread(target=self._clignoter_feux, daemon=True).start()
        print("[FEUX] Feux de detresse ON")

    def desactiver_feux(self):
        if not self.feux_actifs:
            return
        self.stop_feux.set()
        self.feux_actifs = False
        self.leds_gpio.set_all_switch_off()
        self.leds_ws.turn_off_all()
        print("[FEUX] Feux de detresse OFF")

    # ── Moteur ────────────────────────────────────────────────

    def demarrer(self):
        if self.en_marche:
            return
        self.en_marche = True
        self.desactiver_feux()
        self.mc.drive_ramp(self.VITESSE_MARCHE, ramp_time=1.0)
        print("[MOTEUR] Marche avant")

    def arreter(self):
        self.en_marche = False
        self.mc.drive_ramp(0.0, ramp_time=0.00001)
        print("[MOTEUR] Arret")

    # ── Capteur ───────────────────────────────────────────────

    def _surveiller_distance(self):
        while True:
            if self.en_marche:
                dist = self.capteur.checkdist()
                if dist < self.DIST_OBSTACLE_MM:
                    print(f"[CAPTEUR] Obstacle a {dist:.0f} mm — arret !")
                    self.arreter()
                    self.activer_feux()
            time.sleep(self.PERIODE_CAPTEUR)

    # ── Run ───────────────────────────────────────────────────

    def run(self):
        print("=== TACHE 9 : Marche avant avec arret sur obstacle ===")
        print("  M  - demarrer la marche avant")
        print("  A  - arret manuel")
        print("  q  - quitter\n")

        threading.Thread(target=self._surveiller_distance, daemon=True).start()

        try:
            while True:
                cmd = input("Commande > ").strip()
                if cmd == 'M':
                    self.demarrer()
                elif cmd in ('A', 'a'):
                    self.arreter()
                    self.desactiver_feux()
                elif cmd == 'q':
                    break
                else:
                    print("  Commandes : M | A | q")

        except KeyboardInterrupt:
            print("\nFin de programme par Ctrl-C")

        finally:
            self.arreter()          # ← stoppe les moteurs
            self.desactiver_feux()  # ← éteint les LEDs
            self.mc.destroy()       # ← deinit PCA9685


if __name__ == "__main__":
    RobotController().run()