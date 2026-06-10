import tache1 as t1
import tache2 as t2
import tache3 as t3
import tache4 as t4
import tache5 as t5
import tache6 as t6

robot_led_controller = t1.RobotLEDController()
led_controller = t2.LEDController(led_count=14)
servo_controller = t3.ServoController()
servo_sequence = t3.ServoTester(servo_controller)
servo_manual = t3.ServoManual(servo_controller)
motor_controller = t4.MotorController()
distance_sensor = t5.Distance()
line_follower = t6.LineFollower()

action = input("Entrez les numéros de tâche à exécuter séparés d'un espace : ").strip().split()
for i in range(len(action)):
    if action[i] == '1':
        t1.__name__
    elif action[i] == '2':
        t2.__name__
    elif action[i] == '3':
        t3.__name__
    elif action[i] == '4':
        t4.__name__
    elif action[i] == '5':
        t5.__name__
    elif action[i] == '6':
        t6.__name__

