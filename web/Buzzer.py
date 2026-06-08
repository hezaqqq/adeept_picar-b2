#!/usr/bin/env python
# File name   : Buzzer.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/04/19
from gpiozero import TonalBuzzer
import time 
import threading
tb = TonalBuzzer(18)
class Player(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.HAPPY_BIRTHDAY_SONG = [
            ["G4", 0.3], ["G4", 0.3], ["A4", 0.3], ["G4", 0.3], ["C5", 0.3], ["B4", 0.6],
            ["G4", 0.3], ["G4", 0.3], ["A4", 0.3], ["G4", 0.3], ["D5", 0.3], ["C5", 0.6],
            ["G4", 0.3], ["G4", 0.3], ["C5", 0.3], ["B4", 0.3], ["C5", 0.3], ["B4", 0.3], ["A4", 0.6],
            ["F5", 0.3], ["F5", 0.3], ["B4", 0.3], ["C5", 0.3], ["D5", 0.3], ["C5", 0.6]
        ]
        self.SONG_1 = [
                    # Measure 7: "Auf..." (Pickup note)
                    ["Eb4", 0.25], 
                    
                    # Measure 8: "...der Hei - de"
                    ["Ab4", 0.5], ["Ab4", 0.25], ["Bb4", 0.25],
                    
                    # Measure 9: "blüht ein klein - es"
                    ["C5", 0.5], ["C5", 0.25], ["Bb4", 0.25],
                    
                    # Measure 10-11: "Blü - "
                    ["Ab4", 0.5], 
                    # Measure 11: "...me - lein" (Eighth rests on beats 1 and 2)
                    # We use None or just time.sleep in a real loop, but keeping it empty or a pause note works. 
                    # For a simple buzzer, we can just represent rests with "None" or omit if needed.
                    # Let's use a "rest" string so your play loop can handle silent gaps:
                    ["rest", 0.5], ["rest", 0.5], 
                    
                    # Measure 12: (Piano fill / Rest)
                    ["rest", 0.5],
                    
                    # Measure 13: "Und das" (Pickup to Erika)
                    ["Bb4", 0.25], ["Bb4", 0.25],
                    
                    # Measure 14: "heißt..."
                    ["C5", 0.5], 
                    
                    # Measure 15-17: "...E - ri - ka."
                    ["Ab4", 0.25], ["F4", 0.25],  # Measure 15
                    ["Eb4", 0.5],                 # Measure 16
                    ["rest", 0.5],                # Measure 17
                    
                    # Measure 18: "Heiß von" (Pickup)
                    ["Eb4", 0.25], ["Eb4", 0.25],
                    
                    # Measure 19: "hun - dert - tau - send"
                    ["Bb4", 0.5], ["Bb4", 0.25], ["C5", 0.25],
                    
                    # Measure 20: "klein - es"
                    ["Db5", 0.5], ["Db5", 0.25], ["C5", 0.25],
                    
                    # Measure 21-22: "Mäg - "
                    ["Bb4", 0.5],
                    # Measure 22: "...de - lein"
                    ["rest", 0.5], ["rest", 0.5],
                    
                    # Measure 23: "ist mein" (Pickup to the next phrase)
                    ["C5", 0.25], ["Bb4", 0.25]
                ]
        self.__flag = threading.Event()
        self.__flag.clear()
        self.MusicMode = 0

        super(Player, self).__init__(*args, **kwargs)

    def play(self, tune):
        for note, duration in tune:
            if self.MusicMode == 0:
                break
            tb.play(note) 
            time.sleep(float(duration)) 
        tb.stop() 

    def start_playing(self):
        self.MusicMode = 1
        self.resume()

    def pause(self):
        self.__flag.clear()
        tb.stop()
        self.MusicMode = 0

    def resume(self):
        self.__flag.set()

    def run(self):
        while True:
            self.__flag.wait()
            try:
                self.play(self.SONG_1)
            except KeyboardInterrupt:
                self.pause()
                print("Program terminated by user.")

if __name__ == "__main__":
    player = Player()
    player.start()
    player.start_playing() 
    time.sleep(5)
    player.pause()

