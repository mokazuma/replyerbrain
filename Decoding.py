
import glob
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import KFold, GridSearchCV, cross_val_predict, permutation_test_score
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_absolute_error
import nibabel as nib
from nilearn.datasets import load_mni152_template
from nilearn.image import resample_to_img

########################################################################
# set data
########################################################################
template = load_mni152_template(resolution=2)
niinorm = lambda x: resample_to_img(nib.load(x), template).get_fdata()

### from CONN
maskdat = niinorm('seed_lIFG_vox200/Mask.nii')
filelist = sorted(glob.glob('firstlevel/BETA_Subject*_Conditionxxx_Sourcexxx.nii'))

### get feature
feature = pd.DataFrame()
for f in filelist:
    ### whole brain correlation
    dat3d = niinorm(f)

    ### get masked correlation
    bin3d = np.where(maskdat == 0, 0, dat3d)
    seedcor = bin3d[np.nonzero(bin3d)]
    # seedcor.shape

    feature = pd.concat([feature, pd.DataFrame(seedcor).T])

'''set snsdat as twitter data'''
target = snsdat['Reply_network']

########################################################################
# brain decoding
########################################################################
def mlpipe(features, target, cv=10, rand=1, permnumber=None):

    ### make pipeline
    kf = KFold(n_splits=cv, shuffle=True, random_state=rand)
    pipe = Pipeline([("preprocess", StandardScaler()), ("task", Ridge(random_state=rand))])
    search_space = [{"task__alpha": np.logspace(-3, 3, 7)}]
    clf = GridSearchCV(pipe, search_space, cv=cv, verbose=0, n_jobs=-1)

    if permnumber is None:
        ### get prediction result
        cvres = cross_val_predict(clf, features, target, cv=kf, n_jobs=-1)

        return pd.DataFrame({'true': target, 'pred': cvres})
    else:
        ### non-parametric test
        def cor_loss_func(y_true, y_pred):
            r, p = stats.pearsonr(y_true, y_pred)
            return r
        scoretype = make_scorer(cor_loss_func, greater_is_better=True)
        score, perm_scores, pvalue = permutation_test_score(
            clf, features, target, scoring=scoretype, cv=kf, n_permutations=int(permnumber),
            verbose=1, n_jobs=-1)

        return pd.DataFrame({'score': perm_scores})

    
##### machine learning prediction
cv = 2
pred = pd.DataFrame(); stat = pd.DataFrame()
for rr in range(100):
    res = mlpipe(feature, target, cv=cv, rand=rr)
    pred = pd.concat([pred, res.assign(id=range(len(feature)), rand=rr)])
    r, p = stats.pearsonr(res['true'], res['pred'])
    mae = mean_absolute_error(res['true'], res['pred'])
    stat = pd.concat([stat, pd.DataFrame({'r': [r], 'mae': [mae]})])

pred.to_pickle('pred.pkl')
stat.to_pickle('stat.pkl')

##### permutation test
n = 10000
perm = mlpipe(feature, target, cv=cv, permnumber=n)
average = stat['r'].mean()
len(perm.query('score > @average')) / len(perm)  # p-value

perm.to_pickle('perm.pkl')
