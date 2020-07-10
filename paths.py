# Author: Tal Linzen <linzen@nyu.edu>
# License: BSD (3-clause)

import os.path as op

# root = op.dirname(op.dirname(op.abspath(__file__)))
root = '/Users/lauragwilliams/Dropbox/scripts/stimuli_creation'
materials = op.join(root, 'aud', 'materials')
matlab_materials = op.join(root, 'presentation', 'matlab_materials')
elp = op.join(materials, 'ELP_all.csv')
textgrids = op.join(materials, 'TextGrids')
sound_files = op.join(materials, 'sound_files')
stim_props = op.join(materials, 'morph_pred_stim_props.csv')
