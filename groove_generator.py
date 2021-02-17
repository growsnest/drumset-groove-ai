#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, subprocess, shutil, re, pprint
from os.path import basename

# ---- Patterns ----
# Rudiments  ('1' is right hand, '2' is left hand, '0' is note rest)
double_paradiddle = [1,2,1,2,1,1]
paradiddle = [1,2,1,1]
open_stroke = [1,2]
double_stroke_roll = [1,1,2,2]

# One-handed patterns
jazz_ride  = [1,0,0,1,0,1]
jazz_ride2 = [1,0,1,1,0,0]
shuffle = [1,0,1,1,0,1]

time_signatures = [[6,8],[9,8],[12,8],  # triplet-based
                   [2,4],[4,4],[6,4],           # even
                   [3,4],[5,4],[7,4],[9,4],[11,4],[13,4]]   # odd

# ---- Groove for "Reminiscing" by Little River Band ----
groove = {'sig': [4,4],
          'bars': 4,                                     # the number of bars for the longest pattern; use this number
                                                         # to 'fill' bars for shorter patterns (eg snare pattern)
          'bar_grid':             [1,0,0,1,0,0, 1,0,0,1,0,0],   # '1' for quarter note (or beat note in time signature)
          'snare_pattern': {'0': [[0,0,0,0,0,0, 1,0,0,0,0,0],],
                            },
          'kick_pattern':  {'0': [[1,0,0,0,0,0, 0,0,0,0,0,1],
                                  [0,0,1,1,0,0, 0,0,0,0,0,0],
                                  [1,0,0,0,0,0, 0,0,0,0,0,1],
                                  [0,0,1,1,0,0, 0,0,1,0,0,0],],
                            },
          'hihat_pattern': {'0': [[1,0,0,1,0,0, 1,0,0,1,0,0]],    # easy straight quarter notes
                            '1': [[1,0,0,1,0,0, 1,0,0,1,0,1],    # two-bar variation
                                  [0,0,0,1,0,0, 1,0,0,1,0,0],],
                            '2': [[1,0,0,1,0,0, 1,0,0,1,0,1],    # four-bar variation
                                  [0,0,0,1,0,0, 1,0,0,1,0,0],
                                  [1,0,0,1,0,0, 1,0,0,1,0,1],
                                  [0,0,0,1,0,0, 1,0,1,0,0,0],],
                            },
     'open_hihat_pattern': {'0': [[0,0,0,0,0,0, 0,0,0,0,0,0],   # '1' for open hihat foot
                                  [0,0,0,0,0,0, 0,0,0,0,0,0],
                                  [0,0,0,0,0,0, 0,0,0,0,0,1],
                                  [0,0,0,0,0,0, 0,0,1,0,0,0],],
                            },
          'crash_pattern': {'0': [[1,0,0,0,0,0, 0,0,0,0,0,0],
                                  [0,0,0,0,0,0, 0,0,0,0,0,0],
                                  [0,0,0,0,0,0, 0,0,0,0,0,0],
                                  [0,0,0,0,0,0, 0,0,1,0,0,0],],
                            },
          }

# ---- Conventional drum set rules ----
# Conventional is crossed-hands for hihat-based grooves (the verses in songs) and
#   open hands for ride-based grooves (the choruses in songs);
#   dominant side playing (hihat/ride on eighth notes and quarter notes);
# Sticking seems to only apply to the hands, since the feet stay where they are (eg, impossible to play hihat with kick foot)
#
# If hihat and snare play simultaneously, the backbeat hand is on the snare (usually left hand);
#
conventional_drumset_rules_1up_1down = {
    'hihat_groove': {},             # hihat grooves allow both hands on the hihat with exception to snare notes
    'ride_groove': {},              # ride grooves only allow one hand on the ride
    'backbeat_snare': {},              # backbeat snare is played with the same hand (no alternation)

}

# ---- High-to-low tom fill rules ----
# 1) Alternating 16ths require 'R' hand to be the tom-change
# 2) The tom-change hand usually can't be the same hand for the previous tom (for consecutive 16ths)



# ---- Kit layout ---- 1up 1down ----
#
# 'C': Crash cymbal
# 'S': Splash cymbal (or Snare drum)
# 'K': Kick drum
# 'R': Ride cymbal
# 'T': Tomtom
# 'T1': Tomtom1
# 'T2': Tomtom2
# 'F': Floortom
# 'F1': Floortom1
# 'F2': Floortom2
kit_layout = {
    'cymbals':   ['H',' ','C',' ',' ','R',' ','C'],
    'drums':     [' ','S',' ','T','K',' ','F',' '],
}

# ---- Song form ----
# bars in the intro
# bars in the verse
# bars in the chorus
# bars in the bridge
# bars in the outro

# ---- Sample output ---- before embellishments
#             |1..2..3..4..|1..2..3..4..|1..2..3..4..|1..2..3..4..|
# CrashL:     |
# CrashR:     |
# Ride:       |
# HiHat:      |R..R..R..R.R|...R..R..R..|R..R..R..R.R|...R..R.R...|
# Tom:        |
# Snare:      |......L.....|......L.....|......L.....|......L.....|
# Floortom:   |
# Kick:       |o..........o|..oo........|o..........o|..oo....o...|
# Hihat foot: |

# ---- Sample output ---- AFTER embellishments (using the rules)
#             |1..2..3..4..|1..2..3..4..|1..2..3..4..|1..2..3..4..|
# CrashL:     |
# CrashR:     |
# Ride:       |
# HiHat:      |R..R..R..R.R|...R..R..R..|R..R..R..R.R|...R..R.R...|
# Tom:        |
# Snare:      |......L.....|......L.....|......L.....|......L.....|
# Floortom:   |
# Kick:       |o..........o|..oo........|o..........o|..oo....o...|
# Hihat foot: |
