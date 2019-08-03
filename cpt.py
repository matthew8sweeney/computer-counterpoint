# cpt.py
# 9/6/2018
# by Matthew Sweeney
# A program to compose counterpoint.  Perhaps there may sometimes be ways to spend my time that
# feel more pertinent, but I feel like doing this rn, so I can call that into question.

import string
from random import random, choice
from shutil import copyfile

# import music21 as m21
from music21 import pitch, note, chord, scale, key, stream


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


def I64_chords(source):
    """Returns a list of tonic triads in second inversion"""
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


def ii53_chords(source):
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


def IV53_chords(source):
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


def V53_chords(source):
    """Returns a list of possible voicings for a dominant triad in root position"""
    # Calculate all possible notes for each voice
    bPoss = []
    add_note(5, source.brange, bPoss)
    tPoss = []
    for i in triad_range(5):
        add_note(i, source.trange, tPoss)
    aPoss = []
    for i in triad_range(5):
        add_note(i, source.arange, aPoss)
    sPoss = []
    for i in triad_range(5):
        add_note(i, source.srange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss)


def vii6_chords(source):  # TODO touchy subject with the possibility of doubling the LT
    """Returns a list of possible voicings for a leading-tone triad in first inversion"""
    bPoss = []
    add_note(2, source.brange, bPoss)  # or 9
    tPoss = []
    for i in triad_range(7):
        add_note(i, source.trange, tPoss)
    aPoss = []
    for i in triad_range(7):
        add_note(i, source.arange, aPoss)
    sPoss = []
    for i in triad_range(7):
        add_note(i, source.srange, sPoss)

    return Chord_Tree(bPoss, tPoss, aPoss, sPoss, inversion=6)


class SourceSet(scale.ConcreteScale):
    """Collection of pitches that will be used in a composition.
       Knows voice ranges of SATB parts"""
    def __init__(self, *args, **kwargs):
        scale.ConcreteScale.__init__(self, *args, **kwargs)
        self._b_range = self.getChord('g2', 'c4')  # appropriate pitches to define the range of a bass
        self._t_range = self.getChord('d3', 'f4')  # tenor
        self._a_range = self.getChord('c4', 'c5')  # alto
        self._s_range = self.getChord('a4', 'g5')  # soprano

    @property
    def b_range(self):
        return self._b_range.pitches

    @property
    def t_range(self):
        return self._t_range.pitches

    @property
    def a_range(self):
        return self._a_range.pitches

    @property
    def s_range(self):
        return self._s_range.pitches


class ChordTree(list):
    """Remembers possible pitches for each SATB voice in a chord
       Index 0 of each contained list (except the first level/dimension: outside bass) is a note,
       and the succeeding indices are lists (except the last level/dimension: soprano)"""
    def __init__(self, bPoss, tPoss, aPoss, sPoss, inversion=53):
        list.__init__(self)
        self._inversion = inversion
        self._b_pitches = tuple(bPoss)
        self._t_pitches = tuple(tPoss)
        self._a_pitches = tuple(aPoss)
        self._s_pitches = tuple(sPoss)

    @property
    def inversion(self):
        return self._inversion

    @property
    def b_pitches(self):
        return self._b_pitches

    @property
    def t_pitches(self):
        return self._t_pitches

    @property
    def a_pitches(self):
        return self._a_pitches

    @property
    def s_pitches(self):
        return self._s_pitches

    def filter_t(self, bass):
        """Filter out potential tenor note choices that would be incompatible
        with the given bass note"""
        valid_pitches = tuple()
        for tenor in self.t_pitches:
            valid_pitches += (tenor,)
        return valid_pitches

    def filter_a(self, bass, tenor):
        """Filter out potential alto notes not compatible with given bass and tenor"""
        valid_pitches = tuple()
        for alto in self.a_pitches:
            if self.inversion == 53:
                if alto.name != tenor.name:  # Avoid doubling tenor
                    valid_pitches += (alto,)
        return valid_pitches

    def filter_s(self, bass, tenor, alto):
        """Filter out potential sop notes not compatible with
        given bass, tenor, and alto choices"""
        valid_pitches = tuple()
        for sop in self.s_pitches:
            if self.inversion == 53:
                if sop.name != alto.name and sop.name != tenor.name:  # Avoid doubling tenor or alto
                    valid_pitches += (sop,)
        return valid_pitches

    def take_tree_form(self):
        """Expands the sets of possible notes into a tree structure
           representing all possible combinations of choices of the pitches,
           populating the list content of the object"""
        for b in self.b_pitches:
            self.append([b])

        for b in self:
            for t in self.t_pitches:
                b.append([t])

        for b in self:
            for t in b[1:]:  # Element 0 is the bass note
                for a in self.a_pitches:
                    if self.inversion == 53:  # root position -- double the bass
                        if a.name != t[0].name:  # Avoid doubling tenor in alto
                            t.append([a])
                    elif self.inversion == 6:  # first inv -- don't triple the third
                        if not( a.name == b[0].name and a.name == t[0].name ):
                            t.append([a])

        for b in self:
            for t in b[1:]:
                for a in t[1:]:
                    for s in self.s_pitches:
                        if self.inversion == 53:
                            if ( s.name != a[0].name and s.name != t[0].name ): # Avoid doubling tenor or alto in soprano
                                a.append(s)
                        elif self.inversion == 6:  # Not perfect adherence to rules
                            if ( s.name != a[0].name and s.name != t[0].name ):
                                a.append(s)


class ComputerComposition(stream.Stream):
    """Contains a ChordTree in possible_chords for each chord of piece.
       Knows information about its own source set."""
    def __init__(self, src=None, *args, **kwargs):
        stream.Stream.__init__(self, *args, **kwargs)
        self._source_set = src
        self._possible_chords = []

    @property
    def source_set(self):
        return self._source_set

    @property
    def possible_chords(self):
        return self._possible_chords

    def tonic_chord_maj(self):
        """Append a major tonic ChordTree to self"""
        possible_bass_notes = chord.Chord()
        tonic = self.source_set.getTonic()
        for p in self.source_set.b_range:
            if p.name == tonic.name:
                possible_bass_notes.add(pitch.Pitch(p))
            
        possible_tenor_notes = chord.Chord()
        third = pitch.Pitch((tonic.pitchClass + 4) % 12)
        fifth = pitch.Pitch((tonic.pitchClass + 7) % 12)
        for p in self.source_set.t_range:
            if p.name == tonic.name or p.name == third.name or p.name == fifth.name:
                possible_tenor_notes.add(pitch.Pitch(p))

        possible_alto_notes = chord.Chord()
        for p in self.source_set.a_range:
            if p.name == tonic.name or p.name == third.name or p.name == fifth.name:
                possible_alto_notes.add(pitch.Pitch(p))

        possible_soprano_notes = chord.Chord()
        for p in self.source_set.s_range:
            if p.name == tonic.name or p.name == third.name or p.name == fifth.name:
                possible_soprano_notes.add(pitch.Pitch(p))

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_soprano_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s))

    def subdominant_chord_maj(self):
        """Append a major subdominant ChordTree to self"""  # Currently only in root pos
        tonic = self.source_set.getTonic()
        fourth = pitch.Pitch((tonic.pitchClass + 5) % 12)
        sixth = pitch.Pitch((tonic.pitchClass + 9) % 12)

        possible_bass_notes = chord.Chord()
        for bp in self.source_set.b_range:
            if bp.name == fourth.name:
                possible_bass_notes.add(pitch.Pitch(bp))
            
        possible_tenor_notes = chord.Chord()
        for tp in self.source_set.t_range:
            if tp.name == tonic.name or tp.name == fourth.name or tp.name == sixth.name:
                possible_tenor_notes.add(pitch.Pitch(tp))

        possible_alto_notes = chord.Chord()
        for ap in self.source_set.a_range:
            if ap.name == tonic.name or ap.name == fourth.name or ap.name == sixth.name:
                possible_alto_notes.add(pitch.Pitch(ap))

        possible_soprano_notes = chord.Chord()
        for sp in self.source_set.s_range:
            if sp.name == tonic.name or sp.name == fourth.name or sp.name == sixth.name:
                possible_soprano_notes.add(pitch.Pitch(sp))

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_soprano_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s))

    def supertonic_chord_min(self):
        """Append a minor supertonic ChordTree to self"""  # Currently only in root pos
        tonic = self.source_set.getTonic()
        stonic = pitch.Pitch((tonic.pitchClass + 2) % 12)
        fourth = pitch.Pitch((tonic.pitchClass + 5) % 12)
        sixth = pitch.Pitch((tonic.pitchClass + 9) % 12)

        possible_bass_notes = chord.Chord()
        for bp in self.source_set.b_range:
            if bp.name == stonic.name:
                possible_bass_notes.add(pitch.Pitch(bp))
            
        possible_tenor_notes = chord.Chord()
        for tp in self.source_set.t_range:
            if tp.name == stonic.name or tp.name == fourth.name or tp.name == sixth.name:
                possible_tenor_notes.add(pitch.Pitch(tp))

        possible_alto_notes = chord.Chord()
        for ap in self.source_set.a_range:
            if ap.name == stonic.name or ap.name == fourth.name or ap.name == sixth.name:
                possible_alto_notes.add(pitch.Pitch(ap))

        possible_soprano_notes = chord.Chord()
        for sp in self.source_set.s_range:
            if sp.name == stonic.name or sp.name == fourth.name or sp.name == sixth.name:
                possible_soprano_notes.add(pitch.Pitch(sp))

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_soprano_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s))

    def predominant_function_chord(self):
        chord_gen = choice((self.subdominant_chord_maj, self.supertonic_chord_min))  # Later 4
        chord_gen()

    def dominant_function_chord(self):
        choice = int(random() * 1)
        if choice == 0:
            self.append(V53_chords())

    def PACadence(self):  # TODO Write a perfect authentic cadence (even a simple one)
        self.append(I64_chords())
        self.append(V53_chords())
        self.append(I53_chords())

    def realize_tree(self):  # TODO maybe take adjacent chords into consideration here
        """Decide on which possible instance of each chord to actually write.
           uses ChordTree.take_tree_form, an older, unneccessary approach"""
        for chord_tree in self.possible_chords:
            chord_tree.take_tree_form()  # Expand possibilities for this chord tree

            b_list = choice(chord_tree)
            bass = b_list[0]
            t_list = choice(b_list[1:])
            tenor = t_list[0]
            a_list = choice(t_list[1:])
            alto = a_list[0]
            sop = choice(a_list[1:])

            replacement = chord.Chord([bass, tenor, alto, sop])
            self.append(replacement)

    def realize(self):
        for poss_chord in self.possible_chords:  # For each chord in the composition
            b = choice(poss_chord.b_pitches)
            t = choice(poss_chord.filter_t(b))
            a = choice(poss_chord.filter_a(b, t))
            s = choice(poss_chord.filter_s(b, t, a))

            current_chord = chord.Chord([b, t, a, s])
            self.append(current_chord)


def main(phrases=2):
    cMajScale = SourceSet(tonic='c', pitches=['c3', 'd3', 'e3', 'f3', 'g3', 'a3', 'b3', 'c4', \
        'd4', 'e4', 'f4', 'g4', 'a4', 'b4', 'c5', 'd5', 'e5', 'f5', 'g5'])
     
    composition = ComputerComposition(cMajScale)

    composition.tonic_chord_maj()

    composition.predominant_function_chord()
    composition.predominant_function_chord()

    # composition.dominant_function_chord()
    # composition.tonic_chord_maj()
    # composition.predominant_function_chord()

    # for _i in range(phrases - 1):  # TODO Eventually generate middle material
    #     composition.predominant_function_chord()
    #     composition.dominant_function_chord()
    #     composition.tonic_chord_maj()
    #     composition.predominant_function_chord()
    #     composition.dominant_function_chord()
    #     composition.dominant_function_chord()
    #     composition.tonic_chord_maj()
    #     composition.predominant_function_chord()

    # composition.PACadence()  # End on a perfect authentic cadence

    composition.realize()
    composition.write("musicxml", "CompositionV2.xml")


if __name__ == '__main__':
    main()
