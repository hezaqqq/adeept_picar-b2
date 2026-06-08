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

        # --- Sheet music transcription ---
        # Key: D major (F#, C#), Time: 4/4, Tempo: ~160 bpm (approx 0.375s per beat)
        # Source: Piano right-hand melody (soprano saxophone rests throughout intro)
        # Measures 1–12 visible in the score.
        # The piano opens with a rapid ascending figure (marked 8va in m.1),
        # then settles into a repeating rhythmic pattern.
        # Note durations (in seconds) based on ~160 bpm:
        #   quarter = 0.375, eighth = 0.1875, sixteenth = 0.09375, dotted-quarter = 0.5625

        Q  = 0.375    # quarter note
        E  = 0.1875   # eighth note
        S  = 0.09375  # sixteenth note
        DQ = 0.5625   # dotted quarter

        self.SONG_1 = [
            # Measure 1 — fast ascending run (8va, rendered at written pitch)
            # D4 E4 F#4 G4 A4 B4 C#5 D5 (sixteenth-note run) + dotted quarter D5
            ["D4",  S], ["E4",  S], ["F#4", S], ["G4",  S],
            ["A4",  S], ["B4",  S], ["C#5", S], ["D5",  S],
            ["D5",  DQ], ["rest", E],

            # Measure 2 — melodic figure: A4 B4 A4 F#4 | D5 dotted
            ["A4",  E], ["B4",  E], ["A4",  E], ["F#4", E],
            ["D5",  DQ], ["rest", E],

            # Measure 3 — repeat of measure 2 pattern
            ["A4",  E], ["B4",  E], ["A4",  E], ["F#4", E],
            ["D5",  DQ], ["rest", E],

            # Measure 4 — similar figure, ending on E5
            ["A4",  E], ["B4",  E], ["C#5", E], ["A4",  E],
            ["E5",  DQ], ["rest", E],

            # Measure 5 — continues; figure on D5
            ["F#4", E], ["A4",  E], ["D5",  E], ["A4",  E],
            ["D5",  DQ], ["rest", E],

            # Measure 6 — figure on C#5 / A4
            ["E4",  E], ["A4",  E], ["C#5", E], ["A4",  E],
            ["C#5", DQ], ["rest", E],

            # Measure 7 — figure on B4
            ["D4",  E], ["F#4", E], ["B4",  E], ["F#4", E],
            ["B4",  DQ], ["rest", E],

            # Measure 8 — figure resolving back to D5
            ["A4",  E], ["B4",  E], ["A4",  E], ["F#4", E],
            ["D5",  DQ], ["rest", E],

            # Measures 9–12 — piano continues similar pattern (sax still resting)
            # Measure 9
            ["A4",  E], ["B4",  E], ["A4",  E], ["F#4", E],
            ["D5",  DQ], ["rest", E],

            # Measure 10
            ["A4",  E], ["B4",  E], ["C#5", E], ["A4",  E],
            ["E5",  DQ], ["rest", E],

            # Measure 11
            ["F#4", E], ["A4",  E], ["D5",  E], ["A4",  E],
            ["D5",  DQ], ["rest", E],

            # Measure 12 — final measure shown, cadential
            ["E4",  E], ["A4",  E], ["C#5", E], ["A4",  E],
            ["A4",  Q], ["rest", Q],
        ]

        self.__flag = threading.Event()
        self.__flag.clear()
        self.MusicMode = 0

        super(Player, self).__init__(*args, **kwargs)

    def play(self, tune):
        for note, duration in tune:
            if self.MusicMode == 0:
                break
            if note == "rest":
                tb.stop()
            else:
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
    time.sleep(30)
    player.pause()