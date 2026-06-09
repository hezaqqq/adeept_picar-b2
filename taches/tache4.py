#!/usr/bin/env python3
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor

# ── Initialisation ──────────────────────────────────────────
i2c = busio.I2C(SCL, SDA)
pwm_motor = PCA9685(i2c, address=0x5f)
pwm_motor.frequency = 1000  # 1 kHz pour moteurs DC

MOTOR_M1_IN1, MOTOR_M1_IN2 = 15, 14
MOTOR_M2_IN1, MOTOR_M2_IN2 = 12, 13
MOTOR_M3_IN1, MOTOR_M3_IN2 = 11, 10
MOTOR_M4_IN1, MOTOR_M4_IN2 =  8,  9

motor1 = motor.DCMotor(pwm_motor.channels[MOTOR_M1_IN1], pwm_motor.channels[MOTOR_M1_IN2])
motor2 = motor.DCMotor(pwm_motor.channels[MOTOR_M2_IN1], pwm_motor.channels[MOTOR_M2_IN2])
motor3 = motor.DCMotor(pwm_motor.channels[MOTOR_M3_IN1], pwm_motor.channels[MOTOR_M3_IN2])
motor4 = motor.DCMotor(pwm_motor.channels[MOTOR_M4_IN1], pwm_motor.channels[MOTOR_M4_IN2])
for m in (motor1, motor2, motor3, motor4):
    m.decay_mode = motor.SLOW_DECAY

# Servo de direction sur le même PCA9685, canal 0
SERVO_CHANNEL = 0
SERVO_LEFT    = 3277
SERVO_CENTER  = 4915
SERVO_RIGHT   = 6554

# ── Fonctions internes ───────────────────────────────────────
def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

def _set_all_motors(throttle_value):
    for m in (motor1, motor2, motor3, motor4):
        m.throttle = throttle_value

def _set_servo(duty):
    pwm_motor.channels[SERVO_CHANNEL].duty_cycle = int(duty)

# ── Fonction de pilotage avec rampe ─────────────────────────
def drive_ramp(direction, target_speed=25, ramp_time=1.0):
    # direction : 1=avant | -1=arriere | 0=stop
    # target_speed : 0-100%
    # ramp_time : duree montee en vitesse (secondes)
    if direction == 0:
        _set_all_motors(0)
        print("[STOP]")
        return
    target_speed = max(0, min(100, target_speed))
    steps = 100
    delay = ramp_time / steps
    for step in range(1, steps + 1):
        throttle = _map(step, 0, steps, 0.0, target_speed / 100.0)
        _set_all_motors(throttle if direction == 1 else -throttle)
        time.sleep(delay)
    print(f"[{'AVANT' if direction == 1 else 'ARRIERE'}] {target_speed}%  rampe={ramp_time}s")

# ── Etalonnage servo ─────────────────────────────────────────
def calibrate_servo():
    global SERVO_CENTER
    print("\n=== ETALONNAGE SERVO ===")
    print("Balayage automatique...")
    for duty, label in [(SERVO_LEFT, "gauche"), (SERVO_CENTER, "centre"), (SERVO_RIGHT, "droite")]:
        _set_servo(duty)
        print(f"  {label} (duty={duty})")
        time.sleep(1.0)
    _set_servo(SERVO_CENTER)

    center = SERVO_CENTER
    print("\nAjuste le centre (roues droites) : l=gauche | r=droite | ok=valider")
    while True:
        cmd = input(f"  duty={center} > ").strip().lower()
        if cmd == 'ok':
            SERVO_CENTER = center
            print(f"Centre valide : {center}\n")
            break
        elif cmd == 'l':
            center -= 50
            _set_servo(center)
        elif cmd == 'r':
            center += 50
            _set_servo(center)

# ── Arret propre ─────────────────────────────────────────────
def destroy():
    _set_all_motors(0)
    pwm_motor.deinit()

# ── Programme principal : commande manuelle ──────────────────
if __name__ == '__main__':
    speed       = 25   # vitesse courante en %
    ramp_time   = 1.0  # pente courante en secondes
    current_dir = 0    # direction courante

    print("=== COMMANDE MANUELLE ===")
    print("  f/b  - avant/arriere   |  s  - stop")
    print("  +/-  - vitesse +-10%   |  r  - changer la pente")
    print("  c    - etalonner servo  |  q  - quitter")
    print(f"  Vitesse={speed}%  Rampe={ramp_time}s\n")

    try:
        while True:
            cmd = input("Commande > ").strip().lower()
            if cmd == 'q':
                break
            elif cmd == 'f':
                current_dir = 1
                drive_ramp(1, speed, ramp_time)
            elif cmd == 'b':
                current_dir = -1
                drive_ramp(-1, speed, ramp_time)
            elif cmd == 's':
                current_dir = 0
                drive_ramp(0)
            elif cmd == '+':
                speed = min(100, speed + 10)
                print(f"  Vitesse -> {speed}%")
                if current_dir != 0:
                    drive_ramp(current_dir, speed, ramp_time)
            elif cmd == '-':
                speed = max(5, speed - 10)
                print(f"  Vitesse -> {speed}%")
                if current_dir != 0:
                    drive_ramp(current_dir, speed, ramp_time)
            elif cmd == 'r':
                ramp_time = round(max(0.1, ramp_time + 0.5), 1) if ramp_time < 2.0 else 0.1
                print(f"  Rampe -> {ramp_time}s")
            elif cmd == 'c':
                calibrate_servo()
            else:
                print("  Commande inconnue.")
    except KeyboardInterrupt:
        pass
    finally:
        destroy()