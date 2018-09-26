# cpt.py
# 9/6/2018
# by Matthew Sweeney
# A program to compose counterpoint.  Perhaps there may sometimes be ways to spend my time that
# feel more pertenant, but I feel like doing this rn, so I can call that into question.

import string
from random import random

# Using abc notation, from Bass-Clef C to Treble G
majScale = ['C,', 'D,', 'E,', 'F,', 'G,', 'A,', 'B,', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'c', 'd', 'e', 'f', 'g']
bRange = majScale[0:8] # Closest I can get to the range of a bass
tRange = majScale[1:11] # Approximate range of a tenor
aRange = majScale[7:15] # Approximate range of an alto
sRange = majScale[12:] # Approximate range of a soprano


def add_note(func, inv, addTo):
    """Returns a note of harmonic function func (1-7) from pitch inventory inv to list addTo"""
    func = (func - 1) % 7 # Easier to index with 0-6 than 1-7
    i = 0
    while string.ascii_lowercase[i] != inv[0][0].lower():
        i += 1
    phase = i # Offset of inv's starting pitch from 'a' in the alphabet
    j = 0
    while inv[j][0].lower() != majScale[0][0].lower():
        j += 1
    phase = (phase + j) % 7 # Adapt for offset of inv's starting pitch from tonic

    # if func == 6: print("func is 6")
    # Append notes with the correct letter
    for pitch in inv:
        if pitch[0].lower() == string.ascii_lowercase[(func + phase) % 7]:
            addTo.append(pitch)


def triad_range(func):
    return range(func, func + 5, 2)


def first_chord():
    """Returns a random valid voicing of a tonic triad to start on"""
    bPoss = [] # List of possible bass notes

    # Add possible starting bass notes to bPoss
    add_note(1, bRange, bPoss) # Tonic
    add_note(3, bRange, bPoss) # Mediant
    # Select one possible starting bass note randomly
    bass = bPoss[int(random() * len(bPoss))]

    # Add possible starting starting notes for the other three voices
    # Tenor can be 1 3 or 5
    tPoss = []
    add_note(1, tRange, tPoss) # Tonic
    add_note(3, tRange, tPoss) # Mediant
    add_note(5, tRange, tPoss) # Dominant
    # Select one randomly
    tenor = tPoss[int(random() * len(tPoss))]

    # Alto must be one of remaining two triad tones
    aPoss = []
    add_note(1, aRange, aPoss) # Tonic
    add_note(3, aRange, aPoss) # Mediant
    add_note(5, aRange, aPoss) # Dominant
    # Get rid of octaves from tenor
    for i in range(len(aPoss)-1, -1, -1):
        if aPoss[i][0].lower() == tenor[0].lower():
            aPoss.pop(i)
    alto = aPoss[int(random() * len(aPoss))]

    # Soprano must be remaining tone
    sPoss = []
    add_note(1, sRange, sPoss) # Tonic
    add_note(3, sRange, sPoss) # Mediant
    add_note(5, sRange, sPoss) # Dominant
    # Get rid of octaves from tenor and alto
    for i in range(len(sPoss)-1, -1, -1):
        if sPoss[i][0].lower() == tenor[0].lower() or sPoss[i][0].lower() == alto[0].lower():
            sPoss.pop(i)
    soprano = sPoss[int(random() * len(sPoss))]

    return [bass, tenor, alto, soprano]


def IV_chords(inversion=0):
    "Peturns a list of possible voicings for a subdominant triad"


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
    add_note(6, sRange, sPoss)
    
    # Build all chords that can theoretically result from these notes
    # Index 0 of each list (except the first) is a note, and the succeeding indices are lists (except the last - sop)
    chord_tree = []
    for b in range(len(bPoss)):
        chord_tree.append([bPoss[b]])

    for b in range(len(chord_tree)):
        for t in range(len(tPoss)):
            chord_tree[b].append([tPoss[t]])

    for b in range(len(bPoss)):
        for t in range(len(chord_tree[b]) - 1):  # Iterate 1 fewer times because element 0 is the bass note
            for a in range(len(aPoss)):
                if aPoss[a][0].lower() != chord_tree[b][t+1][0][0].lower(): # Avoid doubling tenor in alto
                    chord_tree[b][t+1].append([aPoss[a]])

    for b in range(len(bPoss)):
        for t in range(len(chord_tree[b]) - 1):
            for a in range(len(chord_tree[b][t+1]) - 1): # " because element 0 is the tenor note
                for s in range(len(sPoss)):
                    if (sPoss[s][0].lower() != chord_tree[b][t+1][a+1][0][0].lower() and
                        sPoss[s][0].lower() != chord_tree[b][t+1][0][0].lower()): # Avoid doubling t or a in s
                        chord_tree[b][t+1][a+1].append(sPoss[s])

    print(chord_tree)
    # Eliminate


def main():
    composition = [first_chord()]

    print(composition)
    print(IV53_chords())

main()
