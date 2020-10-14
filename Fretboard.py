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

    def midi_to_str(pitch:int, prefer_flats=False) -> str:
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
            note = 'Db' if prefer_flats else 'C#'
        elif pitch == 2:
            note = 'D'
        elif pitch == 3:
            note = 'Eb' if prefer_flats else 'D#'
        elif pitch == 4:
            note = 'E'
        elif pitch == 5:
            note = 'F'
        elif pitch == 6:
            note = 'Gb' if prefer_flats else 'F#'
        elif pitch == 7:
            note = 'G'
        elif pitch == 8:
            note = 'Ab' if prefer_flats else 'G#'
        elif pitch == 9:
            note = 'A'
        elif pitch == 10:
            note = 'Bb' if prefer_flats else 'A#'
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

    def to_str(self, prefer_flats=False):
        return Note.midi_to_str(self.midi_pitch, prefer_flats=prefer_flats)

    def __str__(self):
        return self.to_str(prefer_flats=False)

class Fretboard:
    # Pixels per mm
    PPMM = 8
    # Colors for each note
    COLORS = {'A':(0.71,0,0), 'B':(0,0.314,0.647), 'C':(0,0.647,0.016), 'D':(0,0.8,0.945), 'E':(0.835,0.627,0),
        'F':(0.675,0.675,0.675), 'G':(0.353,0,0.576), 'frets':(0.2,0.2,0.2), 'strings':(0.6,0.6,0.6)}
    # Variables to let empty spaces on the sides
    WIDTH_RATIO = 1.1
    HEIGHT_RATIO = 1.5

    def __init__(self, tuning:[Note]=[Note('E4'),Note('B3'),Note('G3'),Note('D3'),Note('A2'),Note('E2')],
     scale:int=628, lefty:bool=False, width_nut:int=43, width_twelve:int=52) -> None:
        self.tuning = tuning
        self.scale = scale
        self.lefty = lefty
        self.width_nut = width_nut
        self.width_twelve = width_twelve
        self.fretted_notes = []

    def get_up_dir(self) -> int:
        return -1 if self.lefty else 1

    def get_origin_x(self) -> float:
        return ((Fretboard.WIDTH_RATIO*self.scale/2) - (Fretboard.WIDTH_RATIO-1)*0.5*0.5*self.scale) if self.lefty else (Fretboard.WIDTH_RATIO-1)*0.5*0.5*self.scale

    def get_origin_y(self) -> float:
        return (0.5*(self.width_twelve-self.width_nut + self.width_twelve*(Fretboard.HEIGHT_RATIO-1)))

    def get_fret_pos(self, fret:int) -> float:
        return self.scale*(1-(2**(-float(fret)/12)))

    def get_fret_slot_pos(self, fret:int) -> float:
        return self.scale*(1-(2**(-float(2*fret-1)/24)))

    def get_width_at(self, dist:float) -> float:
        # Height of the triangle formed by the two sides
        h = float(self.width_twelve*self.scale*0.5)/(self.width_twelve-self.width_nut)
        return float(self.width_twelve) * (h-self.scale*0.5+dist) / h

    def fret_string(self, string:int, fret:int) -> None:
        self.fretted_notes.append((string, fret))

    def write_to_png(self, name="out.png", prefer_flats=False) -> None:
        WIDTH = int(self.scale * Fretboard.PPMM * Fretboard.WIDTH_RATIO / 2)
        HEIGHT = int(self.width_twelve * Fretboard.PPMM * Fretboard.HEIGHT_RATIO)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        ctx = cairo.Context(surface)

        # Draw each fret
        ctx.set_source_rgb(*Fretboard.COLORS['frets'])
        for i in range(0, 12+1):
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*self.get_origin_y())
            fret_pos = self.get_fret_pos(i)
            fret_width = self.get_width_at(fret_pos)
            ctx.rel_move_to(self.get_up_dir()*Fretboard.PPMM*fret_pos, -Fretboard.PPMM*(0.5*(fret_width-self.width_nut)))
            ctx.rel_line_to(0, Fretboard.PPMM*fret_width)
        ctx.set_line_width(3*Fretboard.PPMM/4)
        ctx.stroke()

        # Draw fretboard dots
        ctx.set_source_rgb(*Fretboard.COLORS['frets'])
        ctx.set_line_width(3*Fretboard.PPMM/4)
        for i in [3,5,7,9,12]:
            ctx.arc(Fretboard.PPMM*(self.get_origin_x() + self.get_up_dir()*self.get_fret_slot_pos(i)), Fretboard.PPMM*(self.get_origin_y() + 0.5*self.width_nut), Fretboard.PPMM*0.004*self.scale, 0, 2*np.pi)
            ctx.fill()

        # Draw each string
        ctx.set_source_rgb(*Fretboard.COLORS['strings'])
        for i in range(len(self.tuning)):
            ctx.set_line_width(Fretboard.PPMM/2 + i*1.5*Fretboard.PPMM/len(self.tuning))
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*(self.get_origin_y() + i*(self.width_nut/(len(self.tuning)-1))))
            ctx.line_to(Fretboard.PPMM*(Fretboard.WIDTH_RATIO*0.5*self.scale - self.get_origin_x()), Fretboard.PPMM*(self.get_origin_y() - 0.5*(self.width_twelve-self.width_nut) + i*(self.width_twelve/(len(self.tuning)-1))))
            ctx.stroke()

        # Add strings tuning
        font_size = Fretboard.PPMM*1.5*self.width_nut/len(self.tuning)
        for i in range(len(self.tuning)):
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*(self.get_origin_y() + self.width_nut*i/(len(self.tuning)-1)))
            # Retrieve the letter of this note, discarding digits
            n_str = self.tuning[i].to_str(prefer_flats=prefer_flats)
            while(n_str[-1].isdigit()):
                n_str = n_str[:-1]
            ctx.set_source_rgb(*Fretboard.COLORS[n_str[0]])
            ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(font_size)
            _, _, w, h, _, _ = ctx.text_extents(n_str)
            if(self.lefty):
                ctx.rel_move_to(2.5*Fretboard.PPMM, h/2)
            else:
                ctx.rel_move_to(-2.5*Fretboard.PPMM - w, h/2)
            # Finally add text
            ctx.show_text(n_str[0])
            if(len(n_str)>1):
                ctx.select_font_face("Arial", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(0.75*font_size)
                ctx.show_text(n_str[1])

        # Add each note
        for fn in self.fretted_notes:
            # Move to the fret slot of the selected string
            slot_pos = self.get_fret_slot_pos(fn[1])
            ctx.move_to(Fretboard.PPMM*(self.get_origin_x() + self.get_up_dir()*slot_pos), Fretboard.PPMM*(self.get_origin_y() - 0.5*(self.get_width_at(slot_pos)-self.width_nut) + self.get_width_at(slot_pos)*fn[0]/(len(self.tuning)-1)))
            # Compute note
            n = self.tuning[fn[0]]+fn[1]
            # Retrieve the letter of this note, discarding digits
            n_str = n.to_str(prefer_flats=prefer_flats)
            while(n_str[-1].isdigit()):
                n_str = n_str[:-1]
            # Finally add text
            ctx.set_source_rgb(*Fretboard.COLORS[n_str[0]])
            ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(font_size)
            # Move to the corner of the place where the letter will be written
            _, _, w, h, _, _ = ctx.text_extents(n_str)
            ctx.rel_move_to(-w/2, h/2)
            ctx.show_text(n_str[0])
            if(len(n_str)>1):
                ctx.select_font_face("Arial", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(0.75*font_size)
                ctx.show_text(n_str[1])

        surface.write_to_png(name)

if __name__ == '__main__':
    fb = Fretboard(tuning=[Note('E4'),Note('B3'),Note('G3'),Note('D3'),Note('A2'),Note('D2')], lefty=True)
    fb.fret_string(0, 3)
    fb.fret_string(1, 3)
    fb.fret_string(2, 3)
    fb.fret_string(3, 5)
    fb.fret_string(4, 5)
    fb.fret_string(5, 3)
    fb.write_to_png(prefer_flats=True)
