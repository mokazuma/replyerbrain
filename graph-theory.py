
import pandas as pd
import bct
import scipy.io as sio
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests as mlptest
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

#######################################################
# centrality
#######################################################
##### read adjacency matrix from CONN
mridat = sio.loadmat('adjmat.mat')
adjmat_all = pd.DataFrame()
for id in range(mridat['A'].shape[2]):
    adjmat = pd.DataFrame(mridat['A'][:, :, id])
    adjmat_all = pd.concat([adjmat_all, adjmat.assign(ID=id)])

##### read roiname
roiinf = mridat['ROInames'][0]
roi = []
for r in range(len(roiinf)):
    roi += list(roiinf[r])

##### compute centrality
df = lambda x1, x2: pd.DataFrame({'score': x1}).assign(ROI=roi, index=x2)

gt_all = pd.DataFrame()
for s in adjmat_all['ID'].drop_duplicates():
    adjmat_bin = adjmat_all.query('ID==@s').drop('ID', axis=1)
    res = pd.concat([df(bct.degrees_und(adjmat_bin), 'deg'),
                     df(bct.subgraph_centrality(adjmat_bin), 'sub'),
                     df(bct.eigenvector_centrality_und(adjmat_bin), 'eig')])
    gt_all = pd.concat([gt_all, res.assign(subject=s)])

#######################################################
# regression analysis
#######################################################

'''set snsdat as twitter data'''

dv = 'Reply_network'
cntvars = ['year', 'age', 'sex', 'AUDIT', 'FTND', 'SES']
# cntvars = cntvars + ['Big5_E', 'Big5_A', 'Big5_C', 'Big5_N', 'Big5_O',
#                      'IRI_F', 'IRI_PT', 'IRI_EC', 'IRI_PD', 'SHS']

centdf = pd.DataFrame()
for i in gt_all['index'].drop_duplicates():
    roidf = pd.DataFrame()
    for r in gt_all['ROI'].drop_duplicates():
        partdat = gt_all.query('index==@i & ROI==@r').reset_index(drop=True)
        X = pd.concat([partdat[['score']], snsdat[cntvars]], axis=1)

        ### normalization
        scaler.fit(X)
        X_norm = pd.DataFrame(scaler.transform(X)).rename(columns={0: i}).assign(cnt=1)
        ### regression
        model = sm.OLS(snsdat[dv], X_norm)
        res = model.fit()

        df = pd.DataFrame({'beta': res.params, 'SE': res.bse, 't': res.tvalues, 'p': res.pvalues})
        df = pd.DataFrame(df.iloc[0, :]).T
        roidf = pd.concat([roidf, df.assign(ROI=r)])
    centdf = pd.concat([centdf, roidf.assign(pfdr=mlptest(roidf['p'], method='fdr_bh')[1])])

centdf.query('p < .05')
