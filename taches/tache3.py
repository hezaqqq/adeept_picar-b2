#!/usr/bin/env/python3
'''
 SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
# sudo pip3 install adafruit-circuitpython-motor
# sudo pip3 install adafruit-circuitpython-pca9685
'''
import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)
# Create a simple PCA9685 class instance.
pca = PCA9685(i2c, address=0x5f) #default 0x40

pca.frequency = 50

# The pulse range is 750 - 2250 by default. This range typically gives 135 degrees of
# range, but the default is to use 180 degrees. You can specify the expected range if you wish:
# servo7 = servo.Servo(pca.channels[7], actuation_range=135)
def set_angle(ID, angle):
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400,actuation_range=180)
    servo_angle.angle = angle


def test(channel):
    for i in range(180): # The servo turns from 0 to 180 degrees.
        set_angle(channel, i)
        time.sleep(0.01)
    time.sleep(0.5)
    for i in range(180): # The servo turns from 180 to 0 degrees.
        set_angle(channel, 180-i)
        time.sleep(0.01)
    time.sleep(0.5)

if __name__ == "__main__":
    channel = 1
    while True:
        test(channel)



#!/usr/bin/env python3
"""
Tâche 3 – Contrôle des servomoteurs 180° – Robot Adeept PiCar-B
=================================================================
Matériel :
  - Raspberry Pi + Adeept Robot HAT V3.1 (PCA9685 @ I2C 0x5f)
  - CH0, CH1, CH2 : servos mécaniques du robot  ← à utiliser avec précaution
  - CH15           : servo libre (test sans mécanique) ← démarrer ici

Précaution importante :
  Ces servomoteurs ne supportent PAS d'être bloqués en rotation.
  Une butée mécanique provoque une surchauffe rapide et peut les détruire.
  → Toujours rester dans la plage de mouvement réelle du mécanisme.
  → Angles sûrs recommandés pour CH0-CH2 : 60° à 120° (centré sur 90°).
  → CH15 (libre) : 0° à 180° autorisés.

Installation des dépendances :
  sudo pip3 install adafruit-circuitpython-motor adafruit-circuitpython-pca9685
"""

import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

# Initialisation du bus I2C et du contrôleur PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)   # adresse HAT Adeept (défaut PCA9685 = 0x40)
pca.frequency = 50                  # fréquence PWM standard pour servos (50 Hz)

# Constantes de sécurité
# Plages d'angles sûres par canal (min_deg, max_deg)
# Ajuster selon la mécanique réelle du robot
SAFE_ANGLES = {
    0:  (60, 120),   # CH0 – servo mécanique du robot
    1:  (60, 120),   # CH1 – servo mécanique du robot
    2:  (60, 120),   # CH2 – servo mécanique du robot
    15: (0,  180),   # CH15 – servo libre, pas de contrainte mécanique
}

# Paramètres d'impulsion du servo Adeept AD002
MIN_PULSE = 500    # µs – impulsion minimale (0°)
MAX_PULSE = 2400   # µs – impulsion maximale (180°)


# ──────────────────────────────────────────────
# Étape 1 : fonction de base set_angle
# ──────────────────────────────────────────────
def set_angle(servo_id: int, angle: float) -> None:
    """
    Pilote le servomoteur <servo_id> à l'angle <angle> (0° à 180°).

    Paramètres
    ----------
    servo_id : int
        Numéro du canal PCA9685 (0-15).
    angle : float
        Angle cible en degrés, entre 0 et 180.

    Notes
    -----
    - L'angle est clampé dans la plage SAFE_ANGLES du canal pour éviter les butées.
    - Une nouvelle instance servo.Servo est créée à chaque appel
      (comportement identique au code Adeept original).
    """
    # Récupération des limites de sécurité
    min_safe, max_safe = SAFE_ANGLES.get(servo_id, (0, 180))

    # Clamp de l'angle dans la plage de sécurité
    safe_angle = max(min_safe, min(max_safe, angle))

    if safe_angle != angle:
        print(f"  ⚠  CH{servo_id}: angle {angle}° limité à {safe_angle}° "
              f"(plage sûre : {min_safe}°–{max_safe}°)")

    # Création de l'objet servo et envoi de la commande
    s = servo.Servo(
        pca.channels[servo_id],
        min_pulse=MIN_PULSE,
        max_pulse=MAX_PULSE,
        actuation_range=180
    )
    s.angle = safe_angle


# ──────────────────────────────────────────────
# Étape 1 : test sur CH15 (servo libre)
# ──────────────────────────────────────────────
def test_ch15():
    """
    Balayage complet 0° → 180° → 0° sur CH15 (servo libre, sans mécanique).
    À exécuter en premier pour valider le câblage et la communication I2C.
    """
    print("\n── Test CH15 (servo libre) ──")
    print("Balayage 0° → 180°")
    for angle in range(0, 181, 2):
        set_angle(15, angle)
        time.sleep(0.02)
    time.sleep(0.5)

    print("Balayage 180° → 0°")
    for angle in range(180, -1, -2):
        set_angle(15, angle)
        time.sleep(0.02)
    time.sleep(0.5)
    print("Test CH15 terminé.")

# Étape 2 : commande manuelle interactive
def commande_manuelle():
    print("\n" + "═" * 50)
    print("  Commande manuelle des servomoteurs")
    print("  Canaux disponibles : 0, 1, 2 (robot) | 15 (libre)")
    print("  Saisie : <canal> <angle°>  |  'q' pour quitter")
    print("═" * 50)

    # Mise à 90° (centre) de tous les servos au démarrage
    print("\nInitialisation à 90° (centre) …")
    for ch in [0, 1, 2, 15]:
        set_angle(ch, 90)
        time.sleep(0.1)
    print("Prêt.\n")

    while True:
        try:
            saisie = input(">>> ").strip().lower()

            if saisie in ("q", "quit", "exit"):
                print("Sortie – retour à 90° sur tous les canaux.")
                for ch in [0, 1, 2, 15]:
                    set_angle(ch, 90)
                break

            if not saisie:
                continue

            parts = saisie.split()
            if len(parts) != 2:
                print("Format attendu : <canal> <angle>  (ex: 0 90)")
                continue

            canal = int(parts[0])
            angle = float(parts[1])

            if canal not in SAFE_ANGLES:
                print(f"Canal {canal} non disponible. Choisir parmi : {list(SAFE_ANGLES.keys())}")
                continue

            set_angle(canal, angle)
            print(f"  ✓ CH{canal} → {angle}°")

        except ValueError:
            print("Valeur invalide. Exemple de saisie correcte : 1 45")
        except KeyboardInterrupt:
            print("\nInterruption – retour à 90°.")
            for ch in [0, 1, 2, 15]:
                set_angle(ch, 90)
            break

# Point d'entrée
if __name__ == "__main__":
    print("=== Contrôle Servomoteurs – Robot Adeept ===")
    print("Étape 1 : test servo libre CH15")
    test_ch15()

    print("\nÉtape 2 : commande manuelle (CH0, CH1, CH2, CH15)")
    commande_manuelle()

