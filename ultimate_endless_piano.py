# -*- coding: utf-8 -*-
"""Ultimate_Endless_Piano.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/asigalov61/Ultimate-Endless-Piano/blob/main/Ultimate_Endless_Piano.ipynb

# Ultimate Endless Piano (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

#### Project Los Angeles

#### Tegridy Code 2024

***

# (GPU CHECK)
"""

#@title NVIDIA GPU check
!nvidia-smi

"""# (SETUP ENVIRONMENT)"""

#@title Install dependencies
!git clone --depth 1 https://github.com/asigalov61/Ultimate-Endless-Piano
!apt install fluidsynth # pip does not work for some reason. Only apt works

# Commented out IPython magic to ensure Python compatibility.
#@title Import modules

print('=' * 70)
print('Loading core Ultimate Endless Piano modules...')

import os
import copy
from tqdm import notebook
from joblib import Parallel, delayed, parallel_config

print('=' * 70)
print('Loading main Ultimate Endless Piano modules...')
import cupy as cp

# %cd /content/Ultimate-Endless-Piano

import TMIDIX
from midi_to_colab_audio import midi_to_colab_audio
import random

# %cd /content/
print('=' * 70)
print('Loading aux Ultimate Endless Piano modules...')

import matplotlib.pyplot as plt

from sklearn import metrics

from IPython.display import Audio, display

from google.colab import files

print('=' * 70)
print('Creating IO dirs...')

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

print('=' * 70)
print('Done!')
print('Enjoy! :)')
print('=' * 70)

"""# (DOWNLOAD MIDI DATASET)"""

# Commented out IPython magic to ensure Python compatibility.
# @title POP909 MIDI Dataset (best quality of output/recommended)
# %cd /content/Dataset
!git clone https://github.com/music-x-lab/POP909-Dataset
# %cd /content/

# Commented out IPython magic to ensure Python compatibility.
# @title Tegridy Piano MIDI Dataset (best speed/great for quick testing)
# %cd /content/Dataset
!wget https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Tegridy-Piano-CC-BY-NC-SA.zip
!unzip Tegridy-Piano-CC-BY-NC-SA.zip
!rm Tegridy-Piano-CC-BY-NC-SA.zip
# %cd /content/

"""# (SAVE FILE LIST)"""

#@title Save file list
###########

print('=' * 70)
print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset"

filez = list()
for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    for file in filenames:
        if file.endswith(('.mid', '.midi', '.kar')):
            filez.append(os.path.join(dirpath, file))
print('=' * 70)

if filez == []:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

else:
  print('Randomizing file list...')
  random.shuffle(filez)
  print('=' * 70)

  TMIDIX.Tegridy_Any_Pickle_File_Writer(filez, '/content/filez')
  print('=' * 70)

print('Total number of discovered MIDIs:', len(filez))
print('=' * 70)

"""# (LOAD TMIDIX MIDI PROCESSOR)"""

#@title TMIDIX MIDI Processor

print('=' * 70)
print('Loading TMIDIX MIDI Processor...')
print('=' * 70)

def TMIDIX_MIDI_Processor(midi_file):

    try:

        fn = os.path.basename(midi_file)

        #=======================================================
        # START PROCESSING

        raw_score = TMIDIX.midi2single_track_ms_score(midi_file)

        escore_notes = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)

        if escore_notes:

          escore = TMIDIX.augment_enhanced_score_notes(escore_notes[0], timings_divider=32)

          cscore = TMIDIX.chordify_score([1000, escore])

          checked_cscore = TMIDIX.check_and_fix_chords_in_chordified_score(cscore)[0]

          #=======================================================
          # MAIN PROCESSING CYCLE
          #=======================================================

          all_melody_chords = []

          for tv in range(1):

            melody_chords = []
            pitches_chords = []

            pc = checked_cscore[0]

            for c in checked_cscore:

              c.sort(key=lambda x: x[4], reverse=True)

              dtime = max(0, min(127, c[0][1]-pc[0][1]))

              durs = [max(0, min(127, d[2])) for d in c]
              pitches = sorted(set([max(1, min(127, p[4]+tv)) for p in c]), reverse=True)
              vels =  [max(0, min(127, d[5])) for d in c]

              tones_chord = sorted(set([max(1, min(127, p[4]+tv)) % 12 for p in c]))

              if tones_chord in TMIDIX.ALL_CHORDS_SORTED:
                melody_chords.append(TMIDIX.ALL_CHORDS_SORTED.index(tones_chord))
                pitches_chords.append([dtime] + [list(l) for l in zip(durs, pitches, vels)])

              pc = c

            all_melody_chords.append([melody_chords, pitches_chords])

          #=======================================================

          return all_melody_chords

    except Exception as e:
      print(e)
      return None

print('Done!')
print('=' * 70)

"""# (PROCESS MIDIs)"""

#@title Process MIDIs with TMIDIX MIDI processor

NUMBER_OF_PARALLEL_JOBS = 16 # Number of parallel jobs
NUMBER_OF_FILES_PER_ITERATION = 16 # Number of files to queue for each parallel iteration
SAVE_EVERY_NUMBER_OF_ITERATIONS = 160 # Save every 2560 files

print('=' * 70)
print('TMIDIX MIDI Processor')
print('=' * 70)
print('Starting up...')
print('=' * 70)

###########

melody_chords_f = []

files_count = 0
good_files_count = 0

print('Processing MIDI files. Please wait...')
print('=' * 70)

for i in notebook.tqdm_notebook(range(0, len(filez), NUMBER_OF_FILES_PER_ITERATION)):

  with parallel_config(backend='threading', n_jobs=NUMBER_OF_PARALLEL_JOBS, verbose = 0):
    output = Parallel(n_jobs=NUMBER_OF_PARALLEL_JOBS, verbose=0)(delayed(TMIDIX_MIDI_Processor)(f) for f in filez[i:i+NUMBER_OF_FILES_PER_ITERATION])

  for o in output:

      if o is not None:
          melody_chords_f.extend(o)

print('SAVING !!!')
print('=' * 70)
good_files_count += len(melody_chords_f)
print('Saving processed files...')
print('=' * 70)
print('Processed:', good_files_count, 'out of', len(filez), '===', good_files_count / len(filez), 'good files ratio')
print('=' * 70)
count = str(i)
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/Processed_MIDIs')
print('=' * 70)

"""# (LOAD/RELOAD MIDIs)"""

# @title Load/reload processed MIDIs

print('=' * 70)
melody_chords_f = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/Processed_MIDIs')
print('Done!')
print('=' * 70)
print('Number of loaded processed MIDIs:', len(melody_chords_f))
print('=' * 70)

"""# (PREP PROCESSED MIDIs)"""

# @title Prep processed MIDIs
chords_chunks_size = 12 # @param {type:"slider", min:4, max:32, step:1}

print('=' * 70)
print('Preparing chords chunks...')
print('=' * 70)

chunk_size = chords_chunks_size

chords_chunks = []
pitches_chunks = []

intros_idxs = []

total_chunks_count = 0

for c in notebook.tqdm_notebook(melody_chords_f):

  intros_idxs.append(total_chunks_count)

  for i in range(len(c[0])-chunk_size):

    chunk = c[0][i:i+chunk_size]

    chords_chunks.append(chunk)

    pchunk = c[1][i:i+chunk_size]
    pitches_chunks.append(pchunk)

    total_chunks_count += 1

print('=' * 70)
print('Creating main Cupy arrays...')
print('=' * 70)

chords_chunks = cp.array(chords_chunks)
trg_chords_chunks = chords_chunks[:, :-1]

print('Done!')
print('=' * 70)
print('Total number of chords chunks:', len(chords_chunks))
print('=' * 70)

"""# (GENERATE MUSIC)"""

# @title Generate music
start_with_intro = True # @param {type:"boolean"}
number_of_generation_attempts = 100 # @param {type:"slider", min:10, max:200, step:1}
number_of_chords_to_generate = 300 # @param {type:"slider", min:10, max:1000, step:5}
max_overfit_ratio = 0.5 # @param {type:"slider", min:0.1, max:0.9, step:0.1}
chords_memory_length = 16 # @param {type:"slider", min:-1, max:64, step:1}
render_MIDI_to_audio = True # @param {type:"boolean"}
verbose = False # @param {type:"boolean"}

#===============================================================================

num_tries = number_of_generation_attempts
num_chords = number_of_chords_to_generate

#===============================================================================

print('=' * 70)
print('Ultimate Endless Piano Music Generator')
print('=' * 70)
print('Generating...')
print('=' * 70)

for j in notebook.tqdm_notebook(range(num_tries)):

  if start_with_intro:
    src_idx = random.choice(intros_idxs)
  else:
    src_idx = random.randint(0, len(chords_chunks))

  src_chords = chords_chunks[src_idx].tolist()
  src_pitches = pitches_chunks[src_idx]

  new_chords = []
  new_pitches = []

  new_chords.extend(src_chords)
  new_pitches.extend(src_pitches)

  previous_idxs = []
  previous_idxs.append(src_idx)

  counter = 0
  match_ratios = [0]

  for i in range(num_chords):

    src_chunk = cp.array(new_chords[-chunk_size:])

    idxs = cp.where((src_chunk[1:] == trg_chords_chunks).all(axis=1))
    matches_idxs = cp.where(~(src_chunk == chords_chunks[idxs]).all(axis=1))[0]

    if len(matches_idxs) > 0:
      sel_matches_idxs = [id for id in idxs[0][matches_idxs.tolist()].tolist() if id-1 not in previous_idxs and id not in previous_idxs]

      if sel_matches_idxs:

        sel_match_idx = random.choice(sel_matches_idxs)
        sel_match = chords_chunks[sel_match_idx]
        new_chords.append(sel_match.tolist()[-1])
        new_pitches.append(pitches_chunks[sel_match_idx][-1])

        if chords_memory_length > 0:
          previous_idxs.append(sel_match_idx)
          previous_idxs = previous_idxs[-chords_memory_length:]

        elif chords_memory_length == 0:
          previous_idxs = []

        elif chords_memory_length == -1:
          previous_idxs.append(sel_match_idx)

        counter += 1

      else:
        if verbose:
          print('Failed to find good match!!!')
          print('Retrying...')
          print('=' * 70)
        break

    else:
      if verbose:
        print('Failed to find good match!!!')
        print('Retrying...')
        print('=' * 70)
      break

  if counter == num_chords:
    if verbose:
      print('Found possible match!')
      print('Checking...')
      print('=' * 70)

    match_ratios = [0]
    tqdmdis = not verbose
    nchords = cp.array(new_chords)

    for c in notebook.tqdm_notebook(melody_chords_f, disable=tqdmdis):
      comp = cp.array(c[0])
      len_range = min(len(nchords)-1, len(comp)-1)

      # Create a sliding window view of 'comp' with a window length of 'len_range'
      shape = (comp.size - len_range + 1, len_range)
      strides = (comp.strides[0], comp.strides[0])
      windows = cp.lib.stride_tricks.as_strided(comp, shape=shape, strides=strides)

      # Compute match ratios for all windows at once
      match_ratios_chunk = cp.sum(windows == nchords[:len_range], axis=1) / len_range

      match_ratios.extend(match_ratios_chunk.tolist())

      if cp.max(match_ratios_chunk) == 1.0:
        if verbose:
          print('Complete overfit!!!')
          print('Starting new search...')
          print('=' * 70)
        break

      elif max_overfit_ratio < cp.max(match_ratios_chunk) < 1.0:
        if verbose:
          print('High overfit:', cp.max(match_ratios_chunk))
          print('Starting new search...')
          print('=' * 70)
        break

    if 0 < max(match_ratios) <= max_overfit_ratio:
      if verbose:
        print('Found good match!')
        print('Overfit ratio:', max(match_ratios))
        print('=' * 70)
      break

  else:
    if verbose:
      print('Failed to find good match!!!')
      print('Retrying...')
      print('=' * 70)
#===============================================================================

print('=' * 70)

#===============================================================================

if 0 < max(match_ratios) < max_overfit_ratio:

  if not verbose:
    print('Found good match!')
    print('Overfit ratio:', max(match_ratios))

  out1 = new_pitches

  if verbose:
    print('Sample INTs', out1[:12])
    print('=' * 70)

  if len(out1) != 0:

      song = out1
      song_f = []

      time = 0
      dur = 0
      vel = 90
      pitch = 0
      channel = 0

      patches = [0] * 16

      for i, s in enumerate(song):

          time += s[0] * 32

          for d in s[1:]:

            dur = d[0] * 32
            ptc = d[1]
            vel = d[2]

            song_f.append(['note', time, dur, channel, ptc, vel, 0])


  detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Ultimate Endless Piano',
                                                          output_file_name = '/content/Ultimate-Endless-Piano-Composition',
                                                          track_name='Project Los Angeles',
                                                          list_of_MIDI_patches=patches,
                                                          verbose=verbose
                                                          )

  print('=' * 70)
  print('Displaying resulting composition...')
  print('=' * 70)

  fname = '/content/Ultimate-Endless-Piano-Composition'

  if render_MIDI_to_audio:
    midi_audio = midi_to_colab_audio(fname + '.mid')
    display(Audio(midi_audio, rate=16000, normalize=False))

  TMIDIX.plot_ms_SONG(song_f, plot_title=fname)

else:
  print('Nothing to display!')
  print('Please try again...')
  print('=' * 70)

"""# Congrats! You did it! :)"""