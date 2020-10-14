import cairo
import numpy as np

class Note:
    def __init__(self, pitch:str='A4') -> None:
        self.midi_pitch = Note.str_to_midi(pitch)

    def str_to_midi(pitch:str) -> int:
        """example : str_to_midi("A0") = 21"""
        note = pitch[0]
        i = 1
        # Recover string corresponding to note
        while(not pitch[i].isdigit()):
            note += pitch[i]
            i += 1
        # Recover integer corresponding to octave
        octave = int(pitch[i:])
        # Transform note in integer
        if note[0] == 'A':
            offset = 9
        elif note[0] == 'B':
            offset = 11
        elif note[0] == 'C':
            offset = 0
        elif note[0] == 'D':
            offset = 2
        elif note[0] == 'E':
            offset = 4
        elif note[0] == 'F':
            offset = 5
        elif note[0] == 'G':
            offset = 7
        # Handle sharps and flats
        for accidental in note[1:]:
            if accidental == '#':
                offset += 1
            elif accidental == 'b':
                offset -= 1

        return 12 + octave * 12 + offset

    def midi_to_str(pitch:int) -> str:
        # Recover octave
        octave = 0
        while pitch >= 24:
            pitch -= 12
            octave += 1
        # Recover note
        pitch -= 12
        if pitch == 0:
            note = 'C'
        elif pitch == 1:
            note = 'C#'
        elif pitch == 2:
            note = 'D'
        elif pitch == 3:
            note = 'D#'
        elif pitch == 4:
            note = 'E'
        elif pitch == 5:
            note = 'F'
        elif pitch == 6:
            note = 'F#'
        elif pitch == 7:
            note = 'G'
        elif pitch == 8:
            note = 'G#'
        elif pitch == 9:
            note = 'A'
        elif pitch == 10:
            note = 'A#'
        elif pitch == 11:
            note = 'B'
        else:
            note = '?'

        return note+str(octave)

    def __add__(self, other):
        ret = Note(str(self))
        if isinstance(other, int):
            ret.midi_pitch += other
        elif isinstance(other, Note):
            ret.midi_pitch += other.midi_pitch
        elif isinstance(other, str):
            ret.midi_pitch += Note.str_to_midi(other)
        return ret

    def __sub__(self, other):
        ret = Note(str(self))
        if isinstance(other, int):
            ret.midi_pitch -= other
        elif isinstance(other, Note):
            ret.midi_pitch -= other.midi_pitch
        elif isinstance(other, str):
            ret.midi_pitch -= Note.str_to_midi(other)
        return ret

    def __str__(self):
        return Note.midi_to_str(self.midi_pitch)

class Fretboard:
    # Pixels per mm
    PPMM = 4
    # Colors for each note
    COLORS = {'A':(0.71,0,0), 'B':(0,0.314,0.647), 'C':(0,0.647,0.016), 'D':(0,0.8,0.945),
        'E':(0.835,0.627,0), 'F':(0.675,0.675,0.675), 'G':(0.353,0,0.576)}

    def __init__(self, tuning:[Note]=[Note('E2'),Note('A2'),Note('D3'),Note('G3'),Note('B3'),Note('E4')],
     scale:int=628, lefty:bool=False, width_nut:int=43, width_twelve:int=52) -> None:
        self.tuning = tuning
        self.scale = scale
        self.lefty = lefty
        self.width_nut = width_nut
        self.width_twelve = width_twelve
        self.fretted_notes = []

    def get_up_dir(self) -> int:
        return -1 if self.lefty else 1

    def get_origin_x(self) -> int:
        return self.scale/2 if self.lefty else 0

    def get_fret_pos(self, fret:int) -> float:
        return self.scale*(1-(2**(-float(fret)/12)))

    def get_width_at(self, dist:float) -> float:
        # Height of the triangle formed by the two sides
        h = float(self.width_twelve*self.scale*0.5)/(self.width_twelve-self.width_nut)
        return float(self.width_twelve) * (h-self.scale*0.5+dist) / h

    def fret_string(self, string:int, fret:int) -> None:
        self.fretted_notes.append((string, fret))

    def write_to_png(self, name="out.png") -> None:
        WIDTH = 1 + int(self.scale * Fretboard.PPMM / 2)
        HEIGHT = 1 + self.width_twelve * Fretboard.PPMM

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        ctx = cairo.Context(surface)
        #ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

        # Draw each fret
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        for i in range(0, 12+1):
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), 0)
            fret_pos = self.get_fret_pos(i)
            fret_width = self.get_width_at(fret_pos)
            ctx.rel_move_to(self.get_up_dir()*Fretboard.PPMM*fret_pos, Fretboard.PPMM*(0.5*(self.width_twelve-fret_width)))
            ctx.rel_line_to(0, Fretboard.PPMM*fret_width)
        ctx.set_line_width(3*Fretboard.PPMM/4)
        ctx.stroke()

        # Draw each string
        ctx.set_source_rgb(0.6, 0.6, 0.6)
        for i in range(len(self.tuning)):
            ctx.set_line_width(Fretboard.PPMM/2 + i*1.5*Fretboard.PPMM/len(self.tuning))
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*(0.5*(self.width_twelve-self.width_nut) + i*(self.width_nut/(len(self.tuning)-1))))
            if(self.lefty):
                ctx.line_to(0, Fretboard.PPMM*(i*(self.width_twelve/(len(self.tuning)-1))))
            else:
                ctx.line_to(Fretboard.PPMM*self.scale/2, Fretboard.PPMM*(i*(self.width_twelve/(len(self.tuning)-1))))
            ctx.stroke()

        # Add each note
        #cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(Fretboard.PPMM*1.5*self.width_nut/len(self.tuning))
        for fn in self.fretted_notes:
            n = self.tuning[fn[0]]+fn[1]
            n_str = str(n)
            ctx.set_source_rgb(*Fretboard.COLORS[n_str[0]])
            while(n_str[-1].isdigit()):
                n_str = n_str[:-1]
            # TODO
            ctx.move_to(0, Fretboard.PPMM*self.width_twelve)
            ctx.show_text(n_str)

        surface.write_to_png(name)

if __name__ == '__main__':
    fb = Fretboard(lefty=True)
    fb.fret_string(0, 7)
    fb.write_to_png()
