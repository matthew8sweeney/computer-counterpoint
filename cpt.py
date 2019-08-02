# cpt.py
# 9/6/2018
# by Matthew Sweeney
# A program to compose counterpoint.  Perhaps there may sometimes be ways to spend my time that
# feel more pertinent, but I feel like doing this rn, so I can call that into question.

import string
from random import random
from shutil import copyfile

# Using abc notation, from Bass-Clef C to Treble G
majScale = ['C,', 'D,', 'E,', 'F,', 'G,', 'A,', 'B,', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'c', 'd', 'e', 'f', 'g']
bRange = majScale[0:8]  # Closest I can get to the range of a bass
tRange = majScale[1:11]  # Approximate range of a tenor
aRange = majScale[7:15]  # Approximate range of an alto
sRange = majScale[12:]  # Approximate range of a soprano


def add_note(func, inv, addTo):
    """Returns a note of harmonic function func (1-7) from pitch inventory inv to list addTo"""
    func = (func - 1) % 7  # Easier to index with 0-6 than 1-7
    i = 0
    while string.ascii_lowercase[i] != inv[0][0].lower():
        i += 1
    phase = i  # Offset of inv's starting pitch from 'a' in the alphabet
    j = 0
    while inv[j][0].lower() != majScale[0][0].lower():
        j += 1
    phase = (phase + j) % 7  # Adapt for offset of inv's starting pitch from tonic

    # if func == 6: print("func is 6")
    # Append notes with the correct letter
    for pitch in inv:
        if pitch[0].lower() == string.ascii_lowercase[(func + phase) % 7]:
            addTo.append(pitch)


def triad_range(func):
    return range(func, func + 5, 2)


def I53_chords():
    """Returns a list of supertonic triads in root position"""
    bPoss = []
    add_note(1, bRange, bPoss)
    tPoss = []
    for i in triad_range(1):
        add_note(i, tRange, tPoss)
    aPoss = []
    for i in triad_range(1):
        add_note(i, aRange, aPoss)
    sPoss = []
    for i in triad_range(1):
        add_note(i, sRange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss)


def I64_chords():
    """Returns a list of supertonic triads in second inversion"""
    bPoss = []
    add_note(5, bRange, bPoss)
    tPoss = []
    for i in triad_range(1):
        add_note(i, tRange, tPoss)
    aPoss = []
    for i in triad_range(1):
        add_note(i, aRange, aPoss)
    sPoss = []
    for i in triad_range(1):
        add_note(i, sRange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss)


def ii53_chords():
    """Returns a list of supertonic triads in root position"""
    bPoss = []
    add_note(2, bRange, bPoss)
    tPoss = []
    for i in triad_range(2):
        add_note(i, tRange, tPoss)
    aPoss = []
    for i in triad_range(2):
        add_note(i, aRange, aPoss)
    sPoss = []
    for i in triad_range(2):
        add_note(i, sRange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss)


def IV_chords(inversion=0):
    """Returns a list of possible voicings for a subdominant triad"""


def IV53_chords():
    """Returns a list of subdominant triads in root position"""
    # Calculate all possible notes for each voice
    bPoss = []
    add_note(4, bRange, bPoss)
    tPoss = []
    for i in triad_range(4):
        add_note(i, tRange, tPoss) 
    aPoss = []
    for i in triad_range(4):
        add_note(i, aRange, aPoss) 
    sPoss = []
    for i in triad_range(4):
        add_note(i, sRange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss)


def V53_chords():
    """Returns a list of possible voicings for a dominant triad in root position"""
    # Calculate all possible notes for each voice
    bPoss = []
    add_note(5, bRange, bPoss)
    tPoss = []
    for i in triad_range(5):
        add_note(i, tRange, tPoss)
    aPoss = []
    for i in triad_range(5):
        add_note(i, aRange, aPoss)
    sPoss = []
    for i in triad_range(5):
        add_note(i, sRange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss)


def vii6_chords():  # TODO touchy subject with the possibility of doubling the LT
    """Returns a list of possible voicings for a leading-tone triad in first inversion"""
    bPoss = []
    add_note(2, bRange, bPoss)  # or 9
    tPoss = []
    for i in triad_range(7):
        add_note(i, tRange, tPoss)
    aPoss = []
    for i in triad_range(7):
        add_note(i, aRange, aPoss)
    sPoss = []
    for i in triad_range(7):
        add_note(i, sRange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss, inversion=6)


class Chord_Tree(list):
    """Build all chords that can theoretically result from these notes
       Index 0 of each list (except the first level: bass) is a note,
       and the succeeding indices are lists (except the last level: soprano)"""
    def __init__(self, bPoss, tPoss, aPoss, sPoss, inversion=53):
        list.__init__(self)
        for b in bPoss:
            self.append([b])

        for b in self:
            for t in tPoss:
                b.append([t])

        for b in self:
            for t in b[1:]:  # Element 0 is the bass note
                for a in aPoss:
                    if inversion == 53:  # root position -- double the bass
                        if a[0].lower() != t[0].lower():  # Avoid doubling tenor in alto
                            t.append([a])
                    elif inversion == 6:  # first inv -- don't triple the third
                        if not( a[0].lower() == b[0].lower() and
                                a[0].lower() == t[0].lower() ):
                            t.append([a])

        for b in self:
            for t in b[1:]:
                for a in t[1:]:
                    for s in sPoss:
                        if inversion == 53:
                            if ( s[0].lower() != a[0].lower() and  # Avoid doubling tenor or alto in soprano
                                 s[0].lower() != t[0].lower() ):
                                a.append(s)
                        elif inversion == 6:  # Not perfect adherence to rules
                            if ( s[0].lower() != a[0].lower() and
                                 s[0].lower() != t[0].lower() ):
                                a.append(s)


class Composition(list):
    """Contains Chord_Trees as elements"""
    def __init__(self):
        list.__init__(self)
        self.append(self._first_chord())

    def _first_chord(self):
        """Returns a random valid voicing of a tonic triad to start on"""
        bPoss = []  # List of possible bass notes

        # Add possible starting bass notes to bPoss
        add_note(1, bRange, bPoss)  # Tonic
        add_note(3, bRange, bPoss)  # Mediant
        # Select one possible starting bass note randomly
        bass = bPoss[int(random() * len(bPoss))]

        # Add possible starting starting notes for the other three voices
        # Tenor can be 1 3 or 5
        tPoss = []
        add_note(1, tRange, tPoss)  # Tonic
        add_note(3, tRange, tPoss)  # Mediant
        add_note(5, tRange, tPoss)  # Dominant
        # Select one randomly
        tenor = tPoss[int(random() * len(tPoss))]

        # Alto must be one of remaining two triad tones
        aPoss = []
        add_note(1, aRange, aPoss)  # Tonic
        add_note(3, aRange, aPoss)  # Mediant
        add_note(5, aRange, aPoss)  # Dominant
        # Get rid of octaves from tenor
        for i in range(len(aPoss) - 1, -1, -1):
            if aPoss[i][0].lower() == tenor[0].lower():
                aPoss.pop(i)
        alto = aPoss[int(random() * len(aPoss))]

        # Soprano must be remaining tone
        sPoss = []
        add_note(1, sRange, sPoss)  # Tonic
        add_note(3, sRange, sPoss)  # Mediant
        add_note(5, sRange, sPoss)  # Dominant
        # Get rid of octaves from tenor and alto
        for i in range(len(sPoss) - 1, -1, -1):
            if sPoss[i][0].lower() == tenor[0].lower() or sPoss[i][0].lower() == alto[0].lower():
                sPoss.pop(i)
        soprano = sPoss[int(random() * len(sPoss))]

        return [bass, tenor, alto, soprano]

    def tonic_function_chord(self):
        self.append(I53_chords())

    def predominant_function_chord(self):
        choice = int(random() * 2)  # Later 4
        if choice == 0:
            self.append(IV53_chords())
        elif choice == 1:
            self.append(ii53_chords())

    def dominant_function_chord(self):
        choice = int(random() * 1)
        if choice == 0:
            self.append(V53_chords())

    def PACadence(self):  # TODO Write a perfect authentic cadence (even a simple one)
        self.append(I64_chords())
        self.append(V53_chords())
        self.append(I53_chords())

    def realize(self):  # TODO maybe take adjacent chords into consideration here
        """Decide on which possible instance of each chord to actually write"""
        for i, chord in enumerate(self):
            if type(chord[0]) == list:
                possibilities = 0  # Count the possibilities
                for b in chord:
                    for t in b[1:]:
                        for a in t[1:]:
                            possibilities += len(a) - 1
                # Choose a random one (for now)
                choice = int(random() * possibilities)
                # Refactor eventually
                possibility = 0
                for b in chord:
                    for t in b[1:]:
                        for a in t[1:]:
                            for s in a[1:]:
                                if possibility == choice:
                                    replacement = [b[0], t[0], a[0], s]
                                possibility += 1
                self[i] = replacement

    def write_to(self, filename):
        copyfile("cmaj_template.txt", "composition.abc")
        with open(filename, "a") as f:
            for chord in self:
                f.write(f"[{chord[0]}{chord[1]}{chord[2]}{chord[3]}] ")


def main(phrases=2):
    composition = Composition()

    composition.predominant_function_chord()
    composition.predominant_function_chord()
    composition.dominant_function_chord()
    composition.tonic_function_chord()
    composition.predominant_function_chord()

    for _i in range(phrases - 1):  # TODO Eventually generate middle material
        composition.predominant_function_chord()
        composition.dominant_function_chord()
        composition.tonic_function_chord()
        composition.predominant_function_chord()
        composition.dominant_function_chord()
        composition.dominant_function_chord()
        composition.tonic_function_chord()
        composition.predominant_function_chord()

    composition.PACadence()  # End on a perfect authentic cadence

    composition.realize()
    print(composition)
    composition.write_to("composition.abc")


if __name__ == '__main__':
    main()
