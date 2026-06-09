#!/usr/bin/env python3
"""
Tâche 3 – Contrôle des servomoteurs 180° – Robot Adeept PiCar-B
=================================================================
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
  sudo pip3 install adafruit-circuitpython-motor adafruit-circuitpython-pca9685
"""

import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

# ──────────────────────────────────────────────
# Initialisation du bus I2C et du contrôleur PCA9685
# ──────────────────────────────────────────────
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)   # adresse HAT Adeept (défaut PCA9685 = 0x40)
pca.frequency = 50                  # fréquence PWM standard pour servos (50 Hz)

# ──────────────────────────────────────────────
# Constantes de sécurité
# ──────────────────────────────────────────────
# Plages d'angles sûres par canal (min_deg, max_deg)
# ⚠ À ajuster selon la mécanique réelle de votre robot avant tout test sur CH0-CH2
SAFE_ANGLES = {
    0:  (60, 120),   # CH0 – servo mécanique du robot  → ±30° autour du centre
    1:  (60, 120),   # CH1 – servo mécanique du robot  → ±30° autour du centre
    2:  (60, 120),   # CH2 – servo mécanique du robot  → ±30° autour du centre
    7:  (0,  180),   # CH7 – servo libre, pleine plage autorisée
}

# Paramètres d'impulsion du servo Adeept AD002
MIN_PULSE = 500    # µs – impulsion minimale (0°)
MAX_PULSE = 2400   # µs – impulsion maximale (180°)


# ──────────────────────────────────────────────
# Fonction principale : set_angle(servo_id, angle)
# ──────────────────────────────────────────────
def set_angle(servo_id: int, angle: float) -> None:
    """
    Pilote le servomoteur <servo_id> à l'angle <angle> (0° à 180°).

    Paramètres
    ----------
    servo_id : int   – Numéro du canal PCA9685 (0-15)
    angle    : float – Angle cible en degrés (0 à 180)

    Sécurité : l'angle est automatiquement limité à la plage SAFE_ANGLES
    du canal pour éviter toute mise en butée mécanique.
    """
    min_safe, max_safe = SAFE_ANGLES.get(servo_id, (0, 180))

    safe_angle = max(min_safe, min(max_safe, angle))

    if safe_angle != angle:
        print(f"  ⚠  CH{servo_id}: {angle}° limité à {safe_angle}° "
              f"(plage sûre : {min_safe}°–{max_safe}°)")

    s = servo.Servo(
        pca.channels[servo_id],
        min_pulse=MIN_PULSE,
        max_pulse=MAX_PULSE,
        actuation_range=180
    )
    s.angle = safe_angle


# ──────────────────────────────────────────────
# Étape 1 : validation sur CH7 (servo libre)
# ──────────────────────────────────────────────
def test_ch7():
    """
    Test de validation sur CH7 (servo libre, sans contrainte mécanique).
    Séquence : centre (90°) → gauche (45°) → droite (135°) → retour centre (90°).
    But : confirmer que le câblage I2C fonctionne et que set_angle() répond
    correctement, sans risque de blocage.
    """
    print("\n── Étape 1 : validation CH7 (servo libre) ──")
    sequence = [
        (90,  "centre"),
        (45,  "gauche"),
        (135, "droite"),
        (90,  "retour centre"),
    ]
    try:
        for angle, label in sequence:
            print(f"  CH7 → {angle}° ({label})")
            set_angle(7, angle)
            time.sleep(1.0)
        print("  ✓ CH7 OK\n")
    except KeyboardInterrupt:
        print("\nInterruption – retour à 90°.")
        set_angle(7, 90)


# ──────────────────────────────────────────────
# Étape 2 : commande manuelle interactive
# ──────────────────────────────────────────────
def commande_manuelle():
    """
    Interface en ligne de commande pour piloter manuellement
    les servomoteurs CH0, CH1, CH2 et CH7.

    Saisie : <canal> <angle>
    Exemples :
        0 90    → CH0 à 90°  (centre)
        7 45    → CH7 à 45°
        q       → quitter

    L'angle peut être exprimé en degrés (0 à 180).
    """
    print("\n" + "═" * 50)
    print("  Commande manuelle des servomoteurs")
    print("  Canaux disponibles : 0, 1, 2 (robot) | 7 (libre)")
    print("  Saisie : <canal> <angle°>  |  'q' pour quitter")
    print("═" * 50)

    # Mise à 90° (centre) de tous les servos au démarrage
    print("\nInitialisation à 90° (centre) …")
    for ch in [0, 1, 2, 7]:
        set_angle(ch, 90)
        time.sleep(0.1)
    print("Prêt.\n")

    while True:
        try:
            saisie = input(">>> ").strip().lower()

            if saisie in ("q", "quit", "exit"):
                print("Sortie – retour à 90° sur tous les canaux.")
                for ch in [0, 1, 2, 7]:
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
            for ch in [0, 1, 2, 7]:
                set_angle(ch, 90)
            break


# ──────────────────────────────────────────────
# Point d'entrée
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Contrôle Servomoteurs – Robot Adeept ===")
    print("Étape 1 : test servo libre CH7")
    test_ch7()

    print("\nÉtape 2 : commande manuelle (CH0, CH1, CH2, CH7)")
    commande_manuelle()