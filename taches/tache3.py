#!/usr/bin/env python3
"""
Tâche 3 – Contrôle des servomoteurs 180° – Robot Adeept PiCar-B

Matériel :
  - Raspberry Pi + Adeept Robot HAT V3.1 (PCA9685 @ I2C 0x5f)
  - CH0, CH1, CH2 : servos mécaniques du robot  ← à utiliser avec précaution
  - CH7           : servo libre (test sans mécanique) ← démarrer ici

Précaution importante :
  Ces servomoteurs ne supportent PAS d'être bloqués en rotation.
  Une butée mécanique provoque une surchauffe rapide et peut les détruire.
  → Toujours rester dans la plage de mouvement réelle du mécanisme.
  → Angles sûrs recommandés pour CH0-CH2 : 60° à 120° (centré sur 90°).
  → CH7 (libre) : 0° à 180° autorisés.

Installation des dépendances :
  sudo pip3 install adafruit-circuitpython-motor adafruit-circuitpython-pca9685 --break-system-packages
"""

import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

# Classe 1 : ServoController
# Gère le PCA9685 et le pilotage de tous les servomoteurs
class ServoController:
    """
    Contrôleur central des servomoteurs via le PCA9685.

    Attributs
    ---------
    SAFE_ANGLES : dict – plages d'angles sûres par canal (min°, max°)
    MIN_PULSE   : int  – impulsion minimale en µs (position 0°)
    MAX_PULSE   : int  – impulsion maximale en µs (position 180°)
    """

    # Plages d'angles sûres par canal
    SAFE_ANGLES = {
        0: (60, 120),   # CH0 – servo mécanique → ±30° autour du centre (90°)
        1: (60, 120),   # CH1 – servo mécanique → ±30° autour du centre (90°)
        2: (60, 120),   # CH2 – servo mécanique → ±30° autour du centre (90°)
        7: (0,  180),   # CH7 – servo libre, pleine plage autorisée
    }

    MIN_PULSE = 500    # µs – impulsion minimale (0°)
    MAX_PULSE = 2400   # µs – impulsion maximale (180°)

    def __init__(self):
        """Initialise le bus I2C et le contrôleur PCA9685."""
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c, address=0x5f)
        self.pca.frequency = 50
        print("  ✓ PCA9685 initialisé (I2C 0x5f, 50 Hz)")

    def set_angle(self, servo_id: int, angle: float) -> None:
        """
        Pilote le servomoteur <servo_id> à l'angle <angle> (0° à 180°).

        Paramètres
        ----------
        servo_id : int   – Numéro du canal PCA9685 (0–15)
        angle    : float – Angle cible en degrés (0 à 180)

        Sécurité : l'angle est automatiquement limité à la plage SAFE_ANGLES
        du canal pour éviter toute mise en butée mécanique.
        """
        min_safe, max_safe = self.SAFE_ANGLES.get(servo_id, (0, 180))
        safe_angle = max(min_safe, min(max_safe, angle))

        if safe_angle != angle:
            print(f"  ⚠  CH{servo_id}: {angle}° limité à {safe_angle}° "
                  f"(plage sûre : {min_safe}°–{max_safe}°)")

        s = servo.Servo(
            self.pca.channels[servo_id],
            min_pulse=self.MIN_PULSE,
            max_pulse=self.MAX_PULSE,
            actuation_range=180
        )
        s.angle = safe_angle

    def center_all(self) -> None:
        """Remet tous les servos configurés à 90° (position centrale)."""
        for ch in self.SAFE_ANGLES:
            self.set_angle(ch, 90)
            time.sleep(0.1)

    def deinit(self) -> None:
        """Libère proprement le PCA9685."""
        self.pca.deinit()
        print("  PCA9685 libéré.")

# Classe 2 : ServoTester
# Test automatique du servo libre CH7
class ServoTester:
    """
    Effectue un test automatique de validation sur le servo libre CH7.

    Séquence : centre (90°) → gauche (45°) → droite (135°) → retour centre (90°).
    But : confirmer que le câblage I2C fonctionne et que set_angle() répond
    correctement, sans risque de blocage mécanique.
    """
    SEQUENCE = [
        (90,  "centre"),
        (45,  "gauche"),
        (135, "droite"),
        (90,  "retour centre"),
    ]

    def __init__(self, controller: ServoController):
        """
        Paramètres
        controller : ServoController – instance partagée du contrôleur
        """
        self.ctrl = controller

    def run(self) -> None:
        # Lance la séquence de test sur CH7.
        print("\n── Étape 1 : validation CH7 (servo libre) ──")
        try:
            for angle, label in self.SEQUENCE:
                print(f"  CH7 → {angle}° ({label})")
                self.ctrl.set_angle(7, angle)
                time.sleep(1.0)
            print("  ✓ CH7 OK\n")
        except KeyboardInterrupt:
            print("\nInterruption – retour à 90°.")
            self.ctrl.set_angle(7, 90)

# Classe 3 : ServoManual
# Commande manuelle interactive des servomoteurs
class ServoManual:
    """
    Interface en ligne de commande pour piloter manuellement
    les servomoteurs CH0, CH1, CH2 et CH7.

    Saisie : <canal> <angle>
    Exemples :
        0 90    → CH0 à 90° (centre)
        0 60    → CH0 limite gauche
        0 120   → CH0 limite droite
        7 45    → CH7 à 45°
        7 180   → CH7 pleine droite
        q       → quitter
    """

    CHANNELS = [0, 1, 2, 7]

    def __init__(self, controller: ServoController):
        """
        Paramètres
        controller : ServoController – instance partagée du contrôleur
        """
        self.ctrl = controller

    def _afficher_aide(self) -> None:
        # Affiche l'en-tête d'aide au démarrage.
        print("\n" + "═" * 50)
        print("  Commande manuelle des servomoteurs")
        print("  Canaux disponibles : 0, 1, 2 (robot) | 7 (libre)")
        print("  Angles : 0° (gauche) → 90° (centre) → 180° (droite)")
        print("  Saisie : <canal> <angle°>  |  'q' pour quitter")
        print("═" * 50)

    def run(self) -> None:
        # Lance la boucle de commande manuelle.
        self._afficher_aide()

        print("\nInitialisation à 90° (centre) …")
        self.ctrl.center_all()
        print("Prêt.\n")

        while True:
            try:
                saisie = input(">>> ").strip().lower()

                if saisie in ("q", "quit", "exit"):
                    print("Sortie – retour à 90° sur tous les canaux.")
                    self.ctrl.center_all()
                    break

                if not saisie:
                    continue

                parts = saisie.split()
                if len(parts) != 2:
                    print("Format attendu : <canal> <angle>  (ex: 0 90)")
                    continue

                canal = int(parts[0])
                angle = float(parts[1])

                if canal not in self.ctrl.SAFE_ANGLES:
                    print(f"Canal {canal} non disponible. "
                          f"Choisir parmi : {list(self.ctrl.SAFE_ANGLES.keys())}")
                    continue

                self.ctrl.set_angle(canal, angle)
                print(f"  ✓ CH{canal} → {angle}°")

            except ValueError:
                print("Valeur invalide. Exemple de saisie correcte : 1 45")
            except KeyboardInterrupt:
                print("\nInterruption – retour à 90°.")
                self.ctrl.center_all()
                break

# Point d'entrée
if __name__ == "__main__":
    print("=== Contrôle Servomoteurs – Robot Adeept ===\n")

    # Instanciation du contrôleur (partagé entre les deux étapes)
    controller = ServoController()

    # Étape 1 : test automatique servo libre CH7
    print("Étape 1 : test servo libre CH7")
    tester = ServoTester(controller)
    tester.run()

    # Étape 2 : commande manuelle
    print("Étape 2 : commande manuelle (CH0, CH1, CH2, CH7)")
    manual = ServoManual(controller)
    manual.run()

    # Libération propre du matériel
    controller.deinit()