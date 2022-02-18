
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import colorbar
import seaborn as sns
import nibabel as nib
from nilearn import plotting
from surfer import Brain

############################################################################
# Figure 1
############################################################################
col = mcolors.TABLEAU_COLORS
col['black'] = '#000000'

subject_id = 'fsaverage'
surf = 'inflated'
label = pd.read_csv('data/SBC_coord.csv')
''' Social Brain Connectome (SBC): https://neurovault.org/collections/2462/'''

for hemi in ['lh', 'rh']:
    roi = ['PCC', 'PCu', 'aMCC', 'dmPFC', 'frontalpole', 'pMCC', 'rACC', 'vmPFC']
    bilateral = ['AI', 'Cb', 'FFA', 'HC', 'IFG', 'IPL', 'MTG', 'MTV5',
                 'NAcc', 'SMA', 'TPJ', 'amygdala', 'pSTS', 'temporalpole']
    if hemi == 'lh':
        roi.extend(['l'+b for b in bilateral])
    else:
        roi.extend(['r'+b for b in bilateral])

    brain = Brain(subject_id, hemi, surf, background="white")
    for st, en in zip([0, 11], [11, 22]):
        for r, c in zip(roi[st:en], col.keys()):
            coord = label.query('label==@r')
            coord = [list(coord['x'])[0], list(coord['y'])[0], list(coord['z'])[0]]
            brain.add_foci(coord, map_surface="white", color=col[c])

    ##### 3d control & save
    ''' %gui qt '''
    for v in ['med', 'lat']:
        brain.show_view(v)
        brain.save_image('SBC_'+hemi+'-'+v+'.png')

############################################################################
# Figure 3
############################################################################
##### seed-based brain
file = ''' statistical map from CONN '''

sns.set(font_scale=1, style="ticks")
fig, (img_ax, cbar_ax) = plt.subplots(1, 2, figsize=(7, 2),
                                      gridspec_kw={"width_ratios": [10.0, 0.1], "wspace": 0.0})

plotting.plot_stat_map(file, cut_coords=[-2, -52, 26],
                       draw_cross=False, colorbar=False, axes=img_ax)

img = nib.load(file).get_fdata()
img_max = np.max(img)
cbar = colorbar.ColorbarBase(
    cbar_ax,
    ticks=[0, round(img_max)],
    norm=mcolors.Normalize(vmin=0, vmax=img_max),
    orientation="vertical",
    cmap='hot',
    label="$\t{t}$ value"
)
plt.savefig('Figure3a.png')
plt.close()

##### prediction
preddat = pd.read_pickle('result/decoding/pred.pkl')
preddat = preddat.groupby('id').mean()
score = pd.read_pickle('result/decoding/stat.pkl')
r = score['r'].mean()

sns.set(font_scale=1.2, style="ticks")
g = sns.jointplot(x='true', y='pred', kind="reg", data=preddat)
g.set_axis_labels('Actual Reply network size', 'Predicted Reply network size')
g.ax_joint.annotate('$\it{r}$'+' = {:.2f} '.format(r), xy=(-2.5, 1.1), fontsize=22)
plt.tight_layout()
plt.savefig('Figure3b.png')
plt.close()

##### permutation test
perm_score = pd.read_pickle('result/decoding/perm.pkl')

sns.set(font_scale=1.5, style="ticks")
fig = plt.figure(figsize=(9, 7))
plt.hist(perm_score, 20, label='Permutation scores', edgecolor='black', color='m')
ylim = plt.ylim()
plt.plot(2 * [r], ylim, '--b', linewidth=3, label='Prediction Score')
plt.ylim(ylim), plt.legend()
plt.ylabel('Count'), plt.xlabel('Correlation')
plt.tight_layout()
plt.savefig('Figure3c.png')
plt.close()
