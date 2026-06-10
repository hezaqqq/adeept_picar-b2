import time
from gpiozero import LED

# Configuration des GPIO pour chaque LED
LED_CONFIG = {
    1: {"gpio": 9,  "active_high": True},
    2: {"gpio": 25, "active_high": True},
    3: {"gpio": 11, "active_high": True},
    
    4: {"gpio": 0,  "active_high": False},
    5: {"gpio": 19, "active_high": False},
    6: {"gpio": 13, "active_high": False},
    
    7: {"gpio": 1,  "active_high": False},
    8: {"gpio": 5,  "active_high": False},
    9: {"gpio": 6,  "active_high": False},
}

# Dictionnaire pour garder les objets LED créés
leds = {}

# Initialisation des LEDs
def switchSetup():
    global leds
    for led_id, config in LED_CONFIG.items():
        # Crée chaque LED
        leds[led_id] = LED(config["gpio"], active_high=config["active_high"], initial_value=False)

# Allumer ou éteindre une LED
def switch(led_id, status):
    if led_id not in leds:
        print(f"Erreur : La LED {led_id} n'existe pas.")
        return

    if status == 1:
        leds[led_id].on() # Allume
    elif status == 0:
        leds[led_id].off() # Éteint
    else:
        print("Status inconnu")

# Éteindre toutes les LEDs d'un coup
def set_all_switch_off():
    for led_id in leds:
        switch(led_id, 0)


if __name__ == "__main__":
    switchSetup() # On configure les LEDs
    set_all_switch_off() # On éteint tout
    
    print("Commandes : 11-19 (ON), 21-29 (OFF), 0 (Quitter)")
    print("-" * 30)

    # Boucle pour lire les commandes de l'utilisateur
    while True:
        try:
            commande = input("Commande : ").strip()
            
            # Quitter le programme
            if commande == "0":
                set_all_switch_off()
                break
            
            # Vérification du format
            if len(commande) != 2 or not commande.isdigit():
                print("Format invalide")
                continue
                
            # 1er chiffre = action, 2e chiffre = numéro LED
            action = int(commande[0])
            led_id = int(commande[1])
            
            if led_id == 0:
                print("LED invalide")
                continue

            if action == 1:
                switch(led_id, 1) # ON
            elif action == 2:
                switch(led_id, 0) # OFF
            else:
                print("Action inconnue")
                
        except KeyboardInterrupt:
            set_all_switch_off()
            break