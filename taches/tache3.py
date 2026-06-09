#!/usr/bin/env python3
"""
Tâche 3 – Contrôle des servomoteurs 180° – Robot Adeept PiCar-B
=================================================================
Matériel :
  - Raspberry Pi + Adeept Robot HAT V3.1 (PCA9685 @ I2C 0x5f)
  - CH0, CH1, CH2 : servos mécaniques du robot  ← à utiliser avec précaution
  - CH15          : servo libre (test sans mécanique) ← démarrer ici

Précaution importante :
  Ces servomoteurs ne supportent PAS d'être bloqués en rotation.
  Une butée mécanique provoque une surchauffe rapide et peut les détruire.
  → Toujours rester dans la plage de mouvement réelle du mécanisme.
  → Angles sûrs recommandés pour CH0-CH2 : -30° à +30° (centré sur 0°).
  → CH15 (libre) : -90° à +90° autorisés.

Convention d'angle :
    0°   = position centrale
  +90°   = droite (ou haut)
  -90°   = gauche (ou bas)

Installation des dépendances :
  sudo pip3 install adafruit-circuitpython-motor adafruit-circuitpython-pca9685 --break-system-packages
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
# Plages en degrés relatifs (-90° à +90°)
# ⚠ À ajuster selon la mécanique réelle du robot avant tout test sur CH0-CH2
# ──────────────────────────────────────────────
SAFE_ANGLES = {
    0:  (-30, 30),    # CH0 – servo mécanique  → ±30° autour du centre
    1:  (-30, 30),    # CH1 – servo mécanique  → ±30° autour du centre
    2:  (-30, 30),    # CH2 – servo mécanique  → ±30° autour du centre
    15: (-90, 90),    # CH15 – servo libre, pleine plage autorisée
}

# Paramètres d'impulsion du servo Adeept AD002
MIN_PULSE = 500    # µs – impulsion minimale (0°)
MAX_PULSE = 2400   # µs – impulsion maximale (180°)


# ──────────────────────────────────────────────
# Fonction principale : set_angle(servo_id, angle)
# ──────────────────────────────────────────────
def set_angle(servo_id: int, angle: float) -> None:
    """
    Pilote le servomoteur <servo_id> à l'angle <angle>.

    Paramètres
    ----------
    servo_id : int   – Numéro du canal PCA9685 (0-15)
    angle    : float – Angle en degrés relatifs (-90° à +90°)
                       0° = centre, +90° = droite, -90° = gauche

    Sécurité : l'angle est automatiquement limité à la plage SAFE_ANGLES
    du canal pour éviter toute mise en butée mécanique.
    """
    min_safe, max_safe = SAFE_ANGLES.get(servo_id, (-90, 90))

    # Clamp dans la plage de sécurité
    safe_angle = max(min_safe, min(max_safe, angle))

    if safe_angle != angle:
        print(f"  ⚠  CH{servo_id}: {angle}° limité à {safe_angle}° "
              f"(plage sûre : {min_safe}°–{max_safe}°)")

    # Conversion -90/+90 → 0/180 pour le PCA9685
    angle_pwm = safe_angle + 90

    s = servo.Servo(
        pca.channels[servo_id],
        min_pulse=MIN_PULSE,
        max_pulse=MAX_PULSE,
        actuation_range=180
    )
    s.angle = angle_pwm


# ──────────────────────────────────────────────
# Étape 1 : validation sur CH15 (servo libre)
# ──────────────────────────────────────────────
def test_ch15():
    """
    Test de validation sur CH15 (servo libre, sans contrainte mécanique).
    Séquence : centre (0°) → gauche (-45°) → droite (+45°) → retour centre (0°).
    But : confirmer que le câblage I2C fonctionne et que set_angle() répond
    correctement, sans risque de blocage.
    Ctrl+C : arrêt propre avec retour à 0°.
    """
    print("\n── Étape 1 : validation CH15 (servo libre) ──")
    sequence = [
        ( 0,  "centre"),
        (-45, "gauche"),
        (+45, "droite"),
        ( 0,  "retour centre"),
    ]
    try:
        for angle, label in sequence:
            print(f"  CH15 → {angle:+d}° ({label})")
            set_angle(15, angle)
            time.sleep(1.0)
        print("  ✓ CH15 OK\n")
    except KeyboardInterrupt:
        print("\nInterruption – retour à 0°.")
        set_angle(15, 0)


# ──────────────────────────────────────────────
# Étape 2 : commande manuelle interactive
# ──────────────────────────────────────────────
def commande_manuelle():
    """
    Interface en ligne de commande pour piloter manuellement
    les servomoteurs CH0, CH1, CH2 et CH15.

    Saisie : <canal> <angle>
    Exemples :
        0 0      → CH0 au centre
        0 -20    → CH0 légèrement à gauche
        0 +20    → CH0 légèrement à droite
        15 -45   → CH15 à gauche
        15 90    → CH15 pleine droite
        q        → quitter
    """
    print("\n" + "═" * 55)
    print("  Commande manuelle des servomoteurs")
    print("  Canaux disponibles : 0, 1, 2 (robot) | 15 (libre)")
    print("  Angles : -90° (gauche) → 0° (centre) → +90° (droite)")
    print("  Saisie : <canal> <angle°>  |  'q' pour quitter")
    print("═" * 55)

    # Mise à 0° (centre) de tous les servos au démarrage
    print("\nInitialisation à 0° (centre) …")
    for ch in [0, 1, 2, 15]:
        set_angle(ch, 0)
        time.sleep(0.1)
    print("Prêt.\n")

    while True:
        try:
            saisie = input(">>> ").strip().lower()

            if saisie in ("q", "quit", "exit"):
                print("Sortie – retour à 0° (centre) sur tous les canaux.")
                for ch in [0, 1, 2, 15]:
                    set_angle(ch, 0)
                break

            if not saisie:
                continue

            parts = saisie.split()
            if len(parts) != 2:
                print("Format attendu : <canal> <angle>  (ex: 0 -20)")
                continue

            canal = int(parts[0])
            angle = float(parts[1])

            if canal not in SAFE_ANGLES:
                print(f"Canal {canal} non disponible. Choisir parmi : {list(SAFE_ANGLES.keys())}")
                continue

            set_angle(canal, angle)
            print(f"  ✓ CH{canal} → {angle:+.1f}°")

        except ValueError:
            print("Valeur invalide. Exemple de saisie correcte : 1 -20")
        except KeyboardInterrupt:
            print("\nInterruption – retour à 0°.")
            for ch in [0, 1, 2, 15]:
                set_angle(ch, 0)
            break


# ──────────────────────────────────────────────
# Point d'entrée
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Contrôle Servomoteurs – Robot Adeept ===")
    print("Étape 1 : test servo libre CH15")
    test_ch15()

    print("\nÉtape 2 : commande manuelle (CH0, CH1, CH2, CH15)")
    commande_manuelle()