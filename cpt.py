# cpt.py
# 9/6/2018
# by Matthew Sweeney
# A program to compose counterpoint.  Perhaps there may sometimes be ways to spend my time that
# feel more pertinent, but I feel like doing this rn, so I can call that into question.

import string
from base64 import b64encode
from random import random, choice
from shutil import copyfile
from time import time

from music21 import pitch, note, duration, chord, scale, key, stream, metadata


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
            if tenor.midi >= bass.midi:
                valid_pitches += (tenor,)
        return valid_pitches

    def filter_a(self, bass, tenor):
        """Filter out potential alto notes not compatible with given bass and tenor"""
        valid_pitches = tuple()
        for alto in self.a_pitches:
            if self.inversion == 53:
                if alto.midi >= tenor.midi and \
                    alto.pitchClass != tenor.pitchClass:  # Avoid doubling tenor
                    valid_pitches += (alto,)
            elif self.inversion == 64:  # 2nd Inv
                if True:
                    valid_pitches += (alto,)
        return valid_pitches

    def filter_s(self, bass, tenor, alto):
        """Filter out potential sop notes not compatible with
        given bass, tenor, and alto choices"""
        valid_pitches = tuple()
        for sop in self.s_pitches:
            if self.inversion == 53:
                if sop.midi >= alto.midi and \
                    sop.pitchClass != alto.pitchClass and \
                    sop.pitchClass != tenor.pitchClass:  # Avoid doubling tenor or alto
                    valid_pitches += (sop,)
            elif self.inversion == 64:  # 2nd Inv
                if True:
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

    def _select_halfsteps(self, p_ambitus, *halfsteps):
        """Return tuple of pitches within p_ambitus that alighn with specified
        half-steps of the composition's source set (0:tonic, 1:m2nd, 2:M2nd, 3:m3rd, etc.)
        e.g. _select_halfsteps(<ambitus>, 0, 4, 7) for members of tonic M triad"""
        tonic_pitchclass = self.source_set.getTonic().pitchClass
        possible_pitches = tuple()
        halfstep_pitchclasses = []
        for halfstep in halfsteps:
            halfstep_pitchclasses.append(halfstep + tonic_pitchclass)
        for p in p_ambitus:
            if p.pitchClass in halfstep_pitchclasses:
                possible_pitches += (p,)
        return possible_pitches
    
    def tonic_chord_maj(self, inv=53):
        """Append a major tonic ChordTree to self"""
        possible_bass_notes = []
        _tonic = self.source_set.getTonic()
        if inv == 53:
            for p in self.source_set.b_range:
                if p.name == _tonic.name:
                    possible_bass_notes.append(pitch.Pitch(p))
        elif inv == 64:
            for p in self.source_set.b_range:
                if p.pitchClass == (_tonic.pitchClass + 7) % 12:
                    possible_bass_notes.append(pitch.Pitch(p))
            
        possible_tenor_notes = self._select_halfsteps(self.source_set.t_range, 0, 4, 7)
        possible_alto_notes = self._select_halfsteps(self.source_set.a_range, 0, 4, 7)
        possible_sop_notes = self._select_halfsteps(self.source_set.s_range, 0, 4, 7)

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_sop_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s, inv))

    def supertonic_chord_min(self, inv=53):
        """Append a minor supertonic ChordTree to self"""  # Currently only in root pos
        _tonic = self.source_set.getTonic()
        _stonic = pitch.Pitch(_tonic.pitchClass + 2)

        possible_bass_notes = []
        for bp in self.source_set.b_range:
            if bp.name == _stonic.name:
                possible_bass_notes.append(pitch.Pitch(bp))
            
        possible_tenor_notes = self._select_halfsteps(self.source_set.t_range, 2, 5, 9)
        possible_alto_notes = self._select_halfsteps(self.source_set.a_range, 2, 5, 9)
        possible_sop_notes = self._select_halfsteps(self.source_set.s_range, 2, 5, 9)

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_sop_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s, inv))

    def subdominant_chord_maj(self, inv=53):
        """Append a major subdominant ChordTree to self"""  # Currently only in root pos
        _tonic = self.source_set.getTonic()
        _fourth = pitch.Pitch(_tonic.pitchClass + 5)

        possible_bass_notes = []
        for bp in self.source_set.b_range:
            if bp.name == _fourth.name:
                possible_bass_notes.append(pitch.Pitch(bp))
        
        possible_tenor_notes = self._select_halfsteps(self.source_set.t_range, 5, 9, 0)
        possible_alto_notes = self._select_halfsteps(self.source_set.a_range, 5, 9, 0)
        possible_sop_notes = self._select_halfsteps(self.source_set.s_range, 5, 9, 0)

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_sop_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s, inv))

    def dominant_chord_maj(self):
        """Append a major dominant ChordTree to self"""  # Currently only in root pos
        _tonic = self.source_set.getTonic()
        _fourth = pitch.Pitch(_tonic.pitchClass + 5)

        possible_bass_notes = []
        for bp in self.source_set.b_range:
            if bp.name == _fourth.name:
                possible_bass_notes.append(pitch.Pitch(bp))
        
        possible_tenor_notes = self._select_halfsteps(self.source_set.t_range, 7, 11, 2)
        possible_alto_notes  = self._select_halfsteps(self.source_set.a_range, 7, 11, 2)
        possible_sop_notes   = self._select_halfsteps(self.source_set.s_range, 7, 11, 2)

        p_b = possible_bass_notes
        p_t = possible_tenor_notes
        p_a = possible_alto_notes
        p_s = possible_sop_notes 
        self.possible_chords.append(ChordTree(p_b, p_t, p_a, p_s))

    def predominant_function_chord(self):
        chord_gen = choice((
            self.subdominant_chord_maj,
            self.supertonic_chord_min))  # Later 4
        chord_gen()

    def dominant_function_chord(self):
        chord_gen = choice((
            self.dominant_chord_maj,))
        chord_gen()

    def PACadence(self):  # TODO Write a perfect authentic cadence (even a simple one)
        self.tonic_chord_maj(64)
        self.dominant_chord_maj()
        self.tonic_chord_maj()

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
        # Would make sense to insert parts in __init__ but breaks music21 when writing
        for _i in range(2):
            self.insert(0, stream.PartStaff())

        halfnote_chances = {
            len(self.possible_chords) - 1: 0.9,
            len(self.possible_chords) - 2: 0.65,
            len(self.possible_chords) - 3: 0.65,
        }
        past_halfnotes = 0

        for i, poss_chord in enumerate(self.possible_chords):  # For each chord in the composition
            b = choice(poss_chord.b_pitches)
            t = choice(poss_chord.filter_t(b))
            a = choice(poss_chord.filter_a(b, t))
            s = choice(poss_chord.filter_s(b, t, a))

            current_chord_treb = chord.Chord([a, s])
            current_chord_bass = chord.Chord([b, t])

            # Calculate duration offset from beginneing b/c Stream.append() cannot always get it right
            extra_offset_treb = extra_offset_bass = 0 + past_halfnotes

            if i in halfnote_chances:  # If the current chord may become a half note
                if random() < halfnote_chances[i]:
                    current_chord_bass.duration.type = "half"
                    current_chord_treb.duration.type = "half"
                    past_halfnotes += 1
            elif random() < 0.2 and i > 0:  # If this chord is not a potential half note dotted-quarter/eigth
                current_chord_treb.duration.quarterLength -= 0.5
                self.elements[0][i-1].duration.quarterLength += 0.5
                extra_offset_treb += 0.5
            # elif random() < 0.15 and i > 0:  # Bass eigth/dotted-quarter
            #     current_chord_bass.duration.quarterLength += 0.5
            #     self.elements[1][i-1].duration.quarterLength -= 0.5
            #     extra_offset_bass -= 0.5

            self.elements[0].insert(i + extra_offset_treb, current_chord_treb)
            self.elements[1].insert(i + extra_offset_bass, current_chord_bass)


def main(phrases=2):
    cMajScale = SourceSet(tonic='c', pitches=['c3', 'd3', 'e3', 'f3', 'g3', 'a3', 'b3', 'c4', \
        'd4', 'e4', 'f4', 'g4', 'a4', 'b4', 'c5', 'd5', 'e5', 'f5', 'g5'])
     
    composition = ComputerComposition(cMajScale)

    composition.tonic_chord_maj()

    composition.predominant_function_chord()
    composition.predominant_function_chord()
    composition.dominant_function_chord()
    composition.tonic_chord_maj()

    # for _i in range(phrases - 1):  # TODO Eventually generate middle material
    #     composition.predominant_function_chord()
    #     composition.dominant_function_chord()
    #     composition.tonic_chord_maj()
    #     composition.predominant_function_chord()
    #     composition.dominant_function_chord()
    #     composition.dominant_function_chord()
    #     composition.tonic_chord_maj()
    #     composition.predominant_function_chord()

    composition.PACadence()  # End on a perfect authentic cadence

    composition.realize()

    # Add metadata
    composition.insert(0, metadata.Metadata())
    # Showy title
    composition.metadata.title = "Music Fragment " + b64encode(str(time()).encode("ascii")).decode("ascii")
    composition.metadata.composer = "Composed by Computer"

    composition.write("musicxml", "Composition.xml")
    print("done")


if __name__ == '__main__':
    main()
