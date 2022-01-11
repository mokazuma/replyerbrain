
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from nilearn import plotting
from surfer import Brain
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

############################################################################
# Figure 1
############################################################################
col = mcolors.TABLEAU_COLORS
col['black'] = '#000000'

subject_id = 'fsaverage'
surf = 'inflated'
label = pd.read_csv('SBC_coord.csv')

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
plotting.plot_stat_map('seed-basedFC.nii', cut_coords=[-2, -52, 26], draw_cross=False,
                       output_file='Figure3a.png')

##### prediction
preddat = pd.read_pickle('pred.pkl')
preddat = preddat.groupby('id').mean()
scaler.fit(preddat)
x = 'Actual Reply network size'; y = 'Predicted Reply network size'
plotdat = pd.DataFrame(scaler.transform(preddat)).rename(columns={0: x, 1: y})

sns.set(font_scale=1.5, style="ticks")
sns.jointplot(x=x, y=y, kind="reg", data=plotdat)
plt.tight_layout()
plt.savefig('Figure3b.png')
plt.close()

##### permutation test
stat = pd.read_pickle('stat.pkl')
perm = pd.read_pickle('perm.pkl')

sns.set(font_scale=1.75, style="ticks")
fig = plt.figure(figsize=(9, 7))
plt.hist(perm, 20, label='Permutation scores', edgecolor='black', color='m')
ylim = plt.ylim()
plt.plot(2 * [stat['r'].mean()], ylim, '--b', linewidth=3, label='Prediction Score')
plt.ylim(ylim), plt.legend()
plt.ylabel('Count'), plt.xlabel('Correlation')
plt.tight_layout()
plt.savefig('Figure3c.png')
plt.close()
