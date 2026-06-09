#!/usr/bin/env python3
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor


MOTOR_M1_IN1 =  15      #Define the positive pole of M1
MOTOR_M1_IN2 =  14      #Define the negative pole of M1
MOTOR_M2_IN1 =  12      #Define the positive pole of M2
MOTOR_M2_IN2 =  13      #Define the negative pole of M2
MOTOR_M3_IN1 =  11      #Define the positive pole of M3
MOTOR_M3_IN2 =  10      #Define the negative pole of M3
MOTOR_M4_IN1 =  8       #Define the positive pole of M4
MOTOR_M4_IN2 =  9       #Define the negative pole of M4


def map(x,in_min,in_max,out_min,out_max):
  return (x - in_min)/(in_max - in_min) *(out_max - out_min) +out_min

#def setup():
i2c = busio.I2C(SCL, SDA)
# Create a simple PCA9685 class instance.
#  pwm_motor.channels[7].duty_cycle = 0xFFFF
pwm_motor = PCA9685(i2c, address=0x5f) #default 0x40
pwm_motor.frequency = 50

motor1 = motor.DCMotor(pwm_motor.channels[MOTOR_M1_IN1],pwm_motor.channels[MOTOR_M1_IN2] )
motor1.decay_mode = (motor.SLOW_DECAY)
motor2 = motor.DCMotor(pwm_motor.channels[MOTOR_M2_IN1],pwm_motor.channels[MOTOR_M2_IN2] )
motor2.decay_mode = (motor.SLOW_DECAY)
motor3 = motor.DCMotor(pwm_motor.channels[MOTOR_M3_IN1],pwm_motor.channels[MOTOR_M3_IN2] )
motor3.decay_mode = (motor.SLOW_DECAY)
motor4 = motor.DCMotor(pwm_motor.channels[MOTOR_M4_IN1],pwm_motor.channels[MOTOR_M4_IN2] )
motor4.decay_mode = (motor.SLOW_DECAY)



def _set_all_motors(throttle_value):
    for m in (motor1, motor2, motor3, motor4):
        m.throttle = throttle_value


# ──────────────────────────────────────────────
# POINT 1 – Pilotage simple à vitesse fixe
# ──────────────────────────────────────────────
def drive(direction, speed=25):
    """
    Pilotage simple.
    direction :  1 = avant  |  -1 = arrière  |  0 = arrêt
    speed     : 0–100 %  (défaut 25 % pour les premiers tests)
    """
    speed = max(0, min(100, speed))          # clamp 0–100
    throttle = map(speed, 0, 100, 0.0, 1.0)

    if direction == 0:
        _set_all_motors(0)
        print("[DRIVE] Arrêt")
    elif direction == 1:
        _set_all_motors(throttle)
        print(f"[DRIVE] Avant  {speed}%")
    elif direction == -1:
        _set_all_motors(-throttle)
        print(f"[DRIVE] Arrière {speed}%")
    else:
        print("[DRIVE] Direction invalide (utiliser 1, -1 ou 0)")


# ──────────────────────────────────────────────
# POINTS 2 & 3 – Rampe de montée en vitesse
# ──────────────────────────────────────────────
def drive_ramp(direction, target_speed=100, ramp_time=1.0):
    """
    Pilotage avec rampe de montée progressive.

    direction    :  1 = avant  |  -1 = arrière  |  0 = arrêt
    target_speed : vitesse cible 0–100 %
    ramp_time    : durée de la rampe en secondes (défaut 1 s)

    La fonction monte de 0 à target_speed en ramp_time secondes,
    par petits paliers de 1 %, pour éviter les pics de couple.
    """
    if direction == 0:
        drive(0)
        return

    target_speed = max(0, min(100, target_speed))
    steps = 100                              # 100 paliers (résolution 1 %)
    delay = ramp_time / steps

    print(f"[RAMP] Démarrage → {target_speed}% en {ramp_time}s "
          f"({'avant' if direction == 1 else 'arrière'})")

    for step in range(1, steps + 1):
        current_speed = _map(step, 0, steps, 0, target_speed)
        throttle = _map(current_speed, 0, 100, 0.0, 1.0)
        if direction == -1:
            throttle = -throttle
        _set_all_motors(throttle)
        time.sleep(delay)

    print(f"[RAMP] Vitesse atteinte : {target_speed}%")


# ──────────────────────────────────────────────
# POINT 4 – Commande manuelle en terminal
# ──────────────────────────────────────────────
def manual_control():
    """
    Boucle de commande manuelle interactive.
    Commandes :
      f  – avancer        (rampe 1 s)
      b  – reculer        (rampe 1 s)
      s  – stop
      +  – vitesse +10 %
      -  – vitesse -10 %
      q  – quitter
    """
    current_speed = 25          # vitesse initiale conservative
    current_dir   = 0

    print("\n=== COMMANDE MANUELLE ===")
    print("  f  – avancer   |  b  – reculer   |  s  – stop")
    print("  +  – +10 %     |  -  – -10 %     |  q  – quitter")
    print(f"  Vitesse initiale : {current_speed}%\n")

    while True:
        try:
            cmd = input("Commande > ").strip().lower()
        except EOFError:
            break

        if cmd == 'q':
            print("[MANUEL] Fin de la commande manuelle.")
            break
        elif cmd == 'f':
            current_dir = 1
            drive_ramp(current_dir, current_speed, ramp_time=1.0)
        elif cmd == 'b':
            current_dir = -1
            drive_ramp(current_dir, current_speed, ramp_time=1.0)
        elif cmd == 's':
            current_dir = 0
            drive(0)
        elif cmd == '+':
            current_speed = min(100, current_speed + 10)
            print(f"[MANUEL] Vitesse → {current_speed}%")
        elif cmd == '-':
            current_speed = max(5, current_speed - 10)
            print(f"[MANUEL] Vitesse → {current_speed}%")
        else:
            print("[MANUEL] Commande inconnue.")


# ──────────────────────────────────────────────
# POINT 5 – Étalonnage servo de direction
# ──────────────────────────────────────────────
# Valeurs duty_cycle pour PCA9685 à 50 Hz  (résolution 16 bits = 0–65535)
# Pulse standard servo RC :
#   1.0 ms  →  ~3277  (butée gauche)
#   1.5 ms  →  ~4915  (centre)
#   2.0 ms  →  ~6554  (butée droite)
SERVO_LEFT   = 3277
SERVO_CENTER = 4915
SERVO_RIGHT  = 6554

def _set_servo(duty):
    """Envoie une valeur de duty_cycle brute au canal servo."""
    pwm_servo.channels[SERVO_CHANNEL].duty_cycle = int(duty)


def calibrate_servo():
    """
    Étalonnage interactif du servo de direction.

    Étapes :
      1. Balayage automatique gauche → droite pour vérifier le câblage.
      2. Réglage manuel du centre (trim) avec +/- puis validation.
      3. Affichage des valeurs finales à insérer dans le code.
    """
    print("\n=== ÉTALONNAGE SERVO DE DIRECTION ===")
    print("Assure-toi que les roues sont libres de tourner.\n")

    # — Étape 1 : balayage de vérification —
    print("[CALIB] Balayage automatique...")
    _set_servo(SERVO_LEFT)
    print(f"  ← Butée gauche  (duty={SERVO_LEFT})")
    time.sleep(1.0)

    _set_servo(SERVO_CENTER)
    print(f"  ↑ Centre        (duty={SERVO_CENTER})")
    time.sleep(1.0)

    _set_servo(SERVO_RIGHT)
    print(f"  → Butée droite  (duty={SERVO_RIGHT})")
    time.sleep(1.0)

    _set_servo(SERVO_CENTER)
    time.sleep(0.5)

    # — Étape 2 : ajustement du centre —
    center = SERVO_CENTER
    step   = 50          # pas de réglage (~0.05 ms)

    print("\n[CALIB] Ajuste le centre (roues droites) :")
    print("  l  – gauche  |  r  – droite  |  ok  – valider\n")

    while True:
        try:
            cmd = input(f"  duty={center}  > ").strip().lower()
        except EOFError:
            break
        if cmd == 'ok':
            break
        elif cmd == 'l':
            center -= step
            _set_servo(center)
        elif cmd == 'r':
            center += step
            _set_servo(center)
        else:
            print("  Commandes : l / r / ok")

    # — Résumé —
    print("\n[CALIB] ✓ Étalonnage terminé.")
    print(f"  SERVO_LEFT   = {SERVO_LEFT}")
    print(f"  SERVO_CENTER = {center}   ← centre calibré")
    print(f"  SERVO_RIGHT  = {SERVO_RIGHT}")
    print("  → Mets à jour ces constantes dans le script.\n")

    return center


# ──────────────────────────────────────────────
# Arrêt propre
# ──────────────────────────────────────────────
def destroy():
    drive(0)
    _set_servo(SERVO_CENTER)
    pwm_motor.deinit()
    pwm_servo.deinit()
    print("[SYS] Ressources libérées.")


# ──────────────────────────────────────────────
# Programme principal
# ──────────────────────────────────────────────
if __name__ == '__main__':
    try:
        print("=== TEST TÂCHE 4 ===\n")

        # — Séquence de test automatique (faible vitesse) —
        print(">> Test simple à 25%")
        drive(1, speed=25)
        time.sleep(2)
        drive(-1, speed=25)
        time.sleep(2)
        drive(0)
        time.sleep(1)

        # — Test avec rampe —
        print("\n>> Test rampe 0→50% en 1 s (avant)")
        drive_ramp(direction=1, target_speed=50, ramp_time=1.0)
        time.sleep(2)
        print(">> Test rampe 0→50% en 1 s (arrière)")
        drive_ramp(direction=-1, target_speed=50, ramp_time=1.0)
        time.sleep(2)
        drive(0)
        time.sleep(1)

        # — Étalonnage servo —
        print("\n>> Étalonnage servo de direction")
        calibrate_servo()

        # — Commande manuelle —
        print("\n>> Commande manuelle")
        manual_control()

    except KeyboardInterrupt:
        print("\n[SYS] Interruption clavier.")
    finally:
        destroy()