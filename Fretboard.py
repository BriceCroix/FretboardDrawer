import cairo
import numpy as np

class Note:
    """Musical Note

    A class representing a note thanks to its pitch. It easily converts str to notes.
    The strings should be formatted as "XaN" where :
    - X is the musical note, such as 'A', 'B', 'C', ... 'G'
    - a is the optionnal accidental, 'b' or '#'
    - N is the positive integer corresponding to the octave number
    For instance the used string could be 'Bb4'
    """

    class NoteFormatError(Exception):
        def __init__(self):
            self.message = "The given string does not represent a note"
            super().__init__(self.message)

    def __init__(self, pitch:str='A4') -> None:
        self.midi_pitch = Note.str_to_midi(pitch)

    def str_to_midi(pitch:str) -> int:
        """Returns the MIDI pitch corresponding to a given string

        :param pitch : str
            string to convert

        example : str_to_midi("A0") -> 21
        """
        # Recover letter corresponding to note
        note = pitch[0]
        # Recover integer corresponding to octave
        try:
            octave = int(pitch[-1])
        except ValueError:
            raise Note.NoteFormatError
        # Transform note in integer
        if note[0] == 'C':
            offset = 0
        elif note[0] == 'D':
            offset = 2
        elif note[0] == 'E':
            offset = 4
        elif note[0] == 'F':
            offset = 5
        elif note[0] == 'G':
            offset = 7
        elif note[0] == 'A':
            offset = 9
        elif note[0] == 'B':
            offset = 11
        else:
            raise Note.NoteFormatError
        # Handle sharps and flats
        if len(pitch) == 3:
            if pitch[1] == '#':
                offset += 1
            elif pitch[1] == 'b':
                offset -= 1
            else:
                raise Note.NoteFormatError

        return 12 + octave * 12 + offset

    def midi_to_str(pitch:int, prefer_flats=False) -> str:
        """Returns the str corresponding to the given MIDI pitch

        :param pitch : int
            MIDI pitch to convert
        :param prefer_flats : bool
            Will return str with 'b' instead of '#' if true

        example : midi_to_str(22, True) -> 'Bb0'
        """
        # Recover octave
        octave = int(pitch/12)-1
        # Recover note
        pitch %= 12
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

    def is_accidental(self) -> bool:
        """Returns whether or not the note is flat or sharp
        """
        return True if len(self.to_str())==3 else False

    def is_octave(self, other) -> bool:
        """Return whether or not two notes are octaves of each other
        """
        return self.midi_pitch%12 == other.midi_pitch%12

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

    def __eq__(self, other):
        return self.midi_pitch == other.midi_pitch

    def to_str(self, prefer_flats=False) -> str:
        """Returns the str corresponding to the note

        :param prefer_flats : bool
            will return flat instead of sharps if True, for instance 'Bb4' instead of 'A#4'
        """
        return Note.midi_to_str(self.midi_pitch, prefer_flats=prefer_flats)

    def __str__(self) -> str:
        return self.to_str(prefer_flats=False)

class Fretboard:
    """This class represents the fretboard of a string instrument, such as a guitar or a bass

    :param tuning : [Note]
        A list of the notes to which the instrument is tuned to, starting with the highest note. Guitar standard tuning by default.
    :param title : str
        The title of the fretboard diagram
    :param scale : int
        The total scale of the instrument, in millimeters
    :param nb_frets : int
        The number of frets that will be drawn on the diagram
    :param lefty : bool
        Indicates if the instrument is left-handed or not
    :param width_nut : int
        The width of the fretboard at the nut, in millimeters
    :param width_twelve : int
        The width of the fretboard at the twelfth fret, in millimeters
    :param prefer_flats : bool
        Indicates if the accidental notes are displayed as sharp or flats
    :param uku_dots : bool
        Will display ukulele markers intead of guitar ones if true
    """
    # Pixels per mm
    PPMM = 8
    # Colors for each note
    COLORS = {'A':(0.71,0,0), 'B':(0,0.314,0.647), 'C':(0,0.647,0.016), 'D':(0,0.8,0.945), 'E':(0.835,0.627,0),
        'F':(0.675,0.675,0.675), 'G':(0.353,0,0.576), 'frets':(0.2,0.2,0.2), 'strings':(0.2,0.2,0.2), 'title':(0.2,0.2,0.2)}
    # Variables to let empty spaces on the sides
    WIDTH_MARGIN = 10
    HEIGHT_MARGIN = 10
    HEIGHT_TITLE = 20

    def __init__(self, tuning:[Note]=[Note('E4'),Note('B3'),Note('G3'),Note('D3'),Note('A2'),Note('E2')],
     title:str='Fretboard diagram', scale:int=628, nb_frets:int=12, lefty:bool=False,
     width_nut:int=43, width_twelve:int=52, prefer_flats:bool=False, uku_dots:bool=False):
        self.tuning = tuning
        self.title = title
        self.scale = scale
        self.nb_frets = nb_frets
        self.lefty = lefty
        self.width_nut = width_nut
        self.width_twelve = width_twelve
        self.prefer_flats = prefer_flats
        self.uku_dots = uku_dots
        self.fretted_notes = []

    def get_up_dir(self) -> int:
        """Returns the multiplicative integer corresponding to the upper direction, dependinf on the lefty attribute
        """
        return -1 if self.lefty else 1

    def get_origin_x(self) -> float:
        """Returns the x coordinate of the nut
        """
        return (self.get_length() + Fretboard.WIDTH_MARGIN) if self.lefty else (Fretboard.WIDTH_MARGIN + (2**(1/24) -1)*self.get_length())

    def get_origin_y(self) -> float:
        """Returns the y coordinate of the nut
        """
        return (0.5*(self.get_width_at(self.get_fret_pos(self.nb_frets))-self.width_nut) + Fretboard.HEIGHT_TITLE + Fretboard.HEIGHT_MARGIN)

    def get_fret_pos(self, fret:int) -> float:
        """Returns distance in millimeters between the nut and a specific fret

        :param fret : int
            The fret whose position is to be known
        """
        return self.scale*(1-(2**(-float(fret)/12)))

    def get_fret_slot_pos(self, fret:int) -> float:
        """Returns distance in millimeters between the nut and a specific fret slot

        :param fret : int
            The fret whose slot position is to be known
        """
        return self.scale*(1-(2**(-float(2*fret-1)/24)))

    def get_width_at(self, dist:float) -> float:
        """Returns the width of the fretboard at a specific position

        :param dist : float
            The distance in millimeters at which the width is to be known
        """
        # Height of the triangle formed by the two sides
        h = float(self.width_twelve*self.scale*0.5)/(self.width_twelve-self.width_nut)
        return float(self.width_twelve) * (h-self.scale*0.5+dist) / h

    def get_length(self):
        """Returns the total fretboard length
        """
        return self.get_fret_pos(self.nb_frets)

    def fret_all(self, accidental=False):
        """Adds all notes to the fretboard

        :param accidental : bool
            Also adds accidental notes if true
        """
        set = ['A','B','C','D','E','F','G']
        if accidental:
            set += ['A#','C#','D#','F#','G#']
        for n in set:
            self.fret(n, 0)

    def fret(self, arg, string:int=0) -> None:
        """Adds a fretted note to the fretboard

        :param arg : int, str, Note
            Which fret is used, 0 is the open string
            OR a str corresponding to a note such as 'A', 'C#', 'Db4'
            OR a Note object
        :param string : int, optionnal
            Which string is used, all by default, 1 is the highest string

        examples:
            fret(4, 1)
            fret('A#', 3)
            fret('Bb4', 1)
            fret(Note('C#5'), 4)
        """
        if string != 0:
            string_i = string - 1
            if isinstance(arg, int):
                self.fretted_notes.append((string_i, arg))
            elif isinstance(arg, str):
                if arg[-1].isdigit():
                    for i in range(self.nb_frets+1):
                        if self.tuning[string_i]+i == Note(arg):
                            self.fretted_notes.append((string_i, i))
                else:
                    for i in range(self.nb_frets+1):
                        if (self.tuning[string_i]+i).is_octave(Note(arg+'0')):
                            self.fretted_notes.append((string_i, i))

            elif isinstance(arg, Note):
                for i in range(self.nb_frets+1):
                    if self.tuning[string_i]+i == arg :
                        self.fretted_notes.append((string_i, i))
        else:
            # No string given, perform on all strings
            for i in range(1, 1+len(self.tuning)):
                self.fret(arg, i)

    def remove_notes():
        """Removes all fretted notes from the fretboard
        """
        self.fretted_notes() = []

    def write_to_png(self, name="out.png") -> None:
        """Exports the Fretboard to a '.png' file

        :param name : str
            The name of the output file
        """
        WIDTH = int(Fretboard.PPMM*(self.get_length() + 2*Fretboard.WIDTH_MARGIN + (2**(1/24) -1)*self.get_length()))
        HEIGHT = int(Fretboard.PPMM*(self.get_width_at(self.get_fret_pos(self.nb_frets)) + 2*Fretboard.HEIGHT_MARGIN + Fretboard.HEIGHT_TITLE))

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        ctx = cairo.Context(surface)

        # Draw each fret
        fret_line_width = 3*Fretboard.PPMM/4
        ctx.set_source_rgb(*Fretboard.COLORS['frets'])
        for i in range(0, self.nb_frets+1):
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*self.get_origin_y())
            fret_pos = self.get_fret_pos(i)
            fret_width = self.get_width_at(fret_pos)
            ctx.rel_move_to(self.get_up_dir()*Fretboard.PPMM*fret_pos, -Fretboard.PPMM*(0.5*(fret_width-self.width_nut)))
            ctx.rel_line_to(0, Fretboard.PPMM*fret_width)
        ctx.set_line_width(fret_line_width)
        ctx.stroke()

        # Draw each string
        ctx.set_source_rgb(*Fretboard.COLORS['strings'])
        for i in range(len(self.tuning)):
            ctx.set_line_width(Fretboard.PPMM/2 + i*1.5*Fretboard.PPMM/len(self.tuning))
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*(self.get_origin_y() + i*(self.width_nut/(len(self.tuning)-1))))
            ctx.line_to((WIDTH-Fretboard.PPMM*Fretboard.WIDTH_MARGIN) if not self.lefty else Fretboard.PPMM*Fretboard.WIDTH_MARGIN, Fretboard.PPMM*(self.get_origin_y() - 0.5*(self.get_width_at(self.get_length())-self.width_nut) + i*(self.get_width_at(self.get_length())/(len(self.tuning)-1))))
            ctx.stroke()

        # Add strings tuning
        font_size = Fretboard.PPMM*1.5*self.width_nut/len(self.tuning)
        tuning_pos = []
        for i in range(len(self.tuning)):
            ctx.move_to(Fretboard.PPMM*self.get_origin_x(), Fretboard.PPMM*(self.get_origin_y() + self.width_nut*i/(len(self.tuning)-1)))
            # Retrieve the letter of this note, discarding digits
            n_str = self.tuning[i].to_str(prefer_flats=self.prefer_flats)
            n_str = n_str[:-1]
            #ctx.set_source_rgb(*Fretboard.COLORS[n_str[0]])
            ctx.set_source_rgb(*Fretboard.COLORS['strings'])
            ctx.select_font_face("Calibri", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(font_size)
            _, _, w, h, _, _ = ctx.text_extents(n_str)
            if(self.lefty):
                ctx.rel_move_to(2.5*Fretboard.PPMM, h/2)
            else:
                ctx.rel_move_to(-2.5*Fretboard.PPMM - w, h/2)
            tuning_pos.append(ctx.get_current_point())
            # Finally add text
            ctx.show_text(n_str[0])
            if(len(n_str)>1):
                ctx.select_font_face("Calibri", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(0.75*font_size)
                ctx.show_text(n_str[1])

        # Add each note
        font_size_bis = font_size
        # A ratio defining the size of the void around each drawn letter
        letter_margin_ratio = 1.25
        for fn in self.fretted_notes:
            # Move to the fret slot of the selected string
            if fn[1] != 0:
                slot_pos = self.get_fret_slot_pos(fn[1])
                ctx.move_to(Fretboard.PPMM*(self.get_origin_x() + self.get_up_dir()*slot_pos), Fretboard.PPMM*(self.get_origin_y() - 0.5*(self.get_width_at(slot_pos)-self.width_nut) + self.get_width_at(slot_pos)*fn[0]/(len(self.tuning)-1)))
                # Compute note
                n = self.tuning[fn[0]]+fn[1]
                # Retrieve the letter of this note, discarding digits
                n_str = n.to_str(prefer_flats=self.prefer_flats)[:-1]
                # Finally add text
                ctx.set_source_rgb(*Fretboard.COLORS[n_str[0]])
                ctx.select_font_face("Calibri", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                font_size_bis = font_size
                ctx.set_font_size(font_size_bis)
                _, _, w, h, _, _ = ctx.text_extents(n_str)
                # Handle higher frets (smaller space)
                #room = Fretboard.PPMM*(self.get_fret_pos(fn[1]) - self.get_fret_pos(fn[1]-1))
                room = 2*Fretboard.PPMM*(self.get_fret_slot_pos(fn[1]) - self.get_fret_pos(fn[1]-1)) - 2*fret_line_width
                if letter_margin_ratio*w > room:
                    # Lower font size
                    font_size_bis = font_size*room/(letter_margin_ratio*w)
                    ctx.set_font_size(font_size_bis)
                    _, _, w, h, _, _ = ctx.text_extents(n_str)
                # Save position of cursor in order to retrieve it after drawing rectangle
                x, y = ctx.get_current_point()
                # Move to the corner of the place where the letter will be written
                ctx.rel_move_to(-letter_margin_ratio*w/2, -letter_margin_ratio*h/2)
                ctx.set_operator(cairo.OPERATOR_CLEAR)
                # Draw an invisible rectangle, erase string
                ctx.rectangle(*ctx.get_current_point(), letter_margin_ratio*w, letter_margin_ratio*h)
                ctx.fill()
                ctx.set_operator(cairo.OPERATOR_OVER)
                ctx.move_to(x, y)
                # Move to the corner of the place where the letter will be written
                ctx.rel_move_to(-w/2, h/2)
            else:
                # It is an open string
                n_str = self.tuning[fn[0]].to_str(prefer_flats=self.prefer_flats)[:-1]
                ctx.set_source_rgb(*Fretboard.COLORS[n_str[0]])
                ctx.select_font_face("Calibri", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                font_size_bis = font_size
                ctx.set_font_size(font_size_bis)
                ctx.move_to(*tuning_pos[fn[0]])
            # Finally add text
            ctx.show_text(n_str[0])
            if(len(n_str)>1):
                ctx.select_font_face("Calibri", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(0.75*font_size_bis)
                ctx.show_text(n_str[1])

        # Draw fretboard dots
        ctx.set_source_rgb(*Fretboard.COLORS['frets'])
        ctx.set_line_width(3*Fretboard.PPMM/4)
        ctx.set_operator(cairo.OPERATOR_DEST_OVER)
        if self.uku_dots:
            dots = [5,10,15,17]
            ddots = [7,12]
        else:
            dots = [3,5,7,9,15,17,19,21]
            ddots = [12,24]
        for i in dots:
            if i <= self.nb_frets:
                ctx.arc(Fretboard.PPMM*(self.get_origin_x() + self.get_up_dir()*self.get_fret_slot_pos(i)), Fretboard.PPMM*(self.get_origin_y() + 0.5*self.width_nut), Fretboard.PPMM*0.004*self.scale, 0, 2*np.pi)
                ctx.fill()
        for i in ddots:
            if i <= self.nb_frets:
                ctx.arc(Fretboard.PPMM*(self.get_origin_x() + self.get_up_dir()*self.get_fret_slot_pos(i)), Fretboard.PPMM*(self.get_origin_y() + 0.25*self.width_nut), Fretboard.PPMM*0.004*self.scale, 0, 2*np.pi)
                ctx.fill()
                ctx.arc(Fretboard.PPMM*(self.get_origin_x() + self.get_up_dir()*self.get_fret_slot_pos(i)), Fretboard.PPMM*(self.get_origin_y() + 0.75*self.width_nut), Fretboard.PPMM*0.004*self.scale, 0, 2*np.pi)
                ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)

        # Write title
        ctx.move_to(WIDTH/2, Fretboard.HEIGHT_MARGIN)
        ctx.set_source_rgb(*Fretboard.COLORS['title'])
        ctx.select_font_face("Calibri", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(Fretboard.PPMM*Fretboard.HEIGHT_TITLE)
        _, _, w, h, _, _ = ctx.text_extents(self.title)
        # If the title does not fit in the drawing area
        if(w > (WIDTH-2*Fretboard.PPMM*Fretboard.WIDTH_MARGIN)):
            ctx.set_font_size(Fretboard.PPMM*Fretboard.HEIGHT_TITLE*(WIDTH-2*Fretboard.PPMM*Fretboard.WIDTH_MARGIN)/w)
        _, _, w, h, _, _ = ctx.text_extents(self.title)
        # Move to corner of writing area
        ctx.rel_move_to(-w/2, h)
        ctx.show_text(self.title)

        # Finally save image
        surface.write_to_png(name)

################################################################################

if __name__ == '__main__':
    # Creating a standard guitar fretboard, indeed right-handed, showing only four frets
    fb = Fretboard(title = "Open C chord", nb_frets = 4)
    # Printing the open C chord shape, using each string
    fb.fret('E', 1) # Using only the note name
    fb.fret(1, 2) # Using the fret number
    fb.fret(0, 3) # Using the fret number, 0 for open string
    fb.fret(2, 4) # Using the fret number
    fb.fret('C3', 5) # Using the note name and specifying octave
    # Saving image
    fb.write_to_png("C_chord_image.png")

    # Creating a left-handed bass guitar fretboard, in drop D tuning, showing all 21 frets
    fb = Fretboard(tuning=[Note('G2'),Note('D2'),Note('A1'),Note('D1')], title = "Gm chord notes positions (LH)", nb_frets = 21, lefty = True, prefer_flats=True, width_nut=32, width_twelve=45)
    # Printing each notes of a G minor chord on the whole neck
    fb.fret('G') # Using only the note name, not specifying string
    fb.fret('Bb') # Using only the note name, not specifying string
    fb.fret('D') # Using only the note name, not specifying string
    # Saving image
    fb.write_to_png("bass_Gm_notes_LH.png")

    # Creating a left-handed standard guitar fretboard
    fb = Fretboard(title = 'Notes positions on the guitar fretboard (LH)', lefty = True)
    # Adding all non-accidental notes to image
    fb.fret_all(accidental=False)
    fb.write_to_png("Fretboard_notes_LH.png")
