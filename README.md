# Fretboard python module

## The purpose

This python module aims at creating simple yet useful Fretboard diagrams for your string instruments. It allows to highlight some particular notes on the neck. This neck can be adjusted to represent exactly the one of your guitar, bass, ukulele or even 10-strings guitar. Left-handed necks are also supported.

The resolution and color of each element may be modified through the `Fretboard.PPMM` variable and `Fretboard.COLORS` dictionary, although there is no provided method to help you do so.

The `main` part of the provided python file shows examples of how to create some guitar or bass fretboard diagrams with custom tunings and dimensions. Chords diagrams are also an option by representing only a few frets of the fretboard.

## Requirements

- Ultra basic python knowledge (just modify the provided examples in the `main` part)
- `pycairo` module : install using pip `python3 -m pip install pycairo`
- `numpy` module : install using pip `python3 -m pip install numpy`
