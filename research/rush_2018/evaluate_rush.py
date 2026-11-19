"""Run from any directory using Python, pandas, numpy and pyarrow."""
from pathlib import Path
from functools import lru_cache
import pandas as pd
import numpy as np
def cdist(a,b,metric): return np.abs(a[:,None,:]-b[None,:,:]).max(axis=2)

folder = Path(__file__).resolve().parent
root = folder.parents[1]
codes = pd.read_csv(folder/'proposal_codes.csv', dtype=str)
lists = [set(codes.loc[codes.proposal == name, 'hs8']) for name in ('April','June','July')]
assert [len(group) for group in lists] == [1333,284,6031]
@lru_cache(None)
def month(period):
    d=pd.read_parquet(root/'panel'/'hs8'/f'{period}.parquet',columns=['cty','hs8','value','qty','qty_ok','unit'])
    return d[d.cty.astype(str)=='5700'].set_index('hs8')

def wave(year,cut,target,group):
    p=pd.Period(f'{year}-{cut:02}',freq='M')
    t=pd.Period(f'{year}-{target:02}',freq='M')
    periods=[p-2,p-1,p]
    def total(offset):return pd.concat([month(m-offset).value for m in periods],axis=1).sum(axis=1)
    d=pd.DataFrame({'prior':total(12),'recent':total(0),'base':month(t-12).value,'actual':month(t).value})
    d=d.fillna(0).query('prior>0 and base>0').copy()
    d['score']=d.recent/d.prior
    d['jump']=d.actual/d.base>1.25
    q0,q1=month(t-12),month(t)
    valid=q0.qty_ok & (q0.qty>0) & (q0.unit==q1.unit.reindex(q0.index)) & q1.qty_ok.reindex(q0.index,fill_value=False)
    qr=q1.qty/q0.qty
    qr=qr.where(valid)
    # zero trade is zero quantity, regardless of base physical unit
    zeros=q0.index[q0.qty_ok & (q0.qty>0) & ~q0.index.isin(q1.index)]
    qr.loc[zeros]=0
    d['qjump']=(qr>1.25).where(qr.notna()).reindex(d.index)
    d['ch4']=d.index.str[:4]
    g=d[d.index.isin(lists[group])]
    picks=g.nlargest(round(len(g)*.2),'score')
    print(year,target,'eligible',len(g),'selected',len(picks),'dollars',round(g.jump.mean()*100,1),round(picks.jump.mean()*100,1),'qty',g.qjump.count(),picks.qjump.count(),round(g.qjump.mean()*100,1),round(picks.qjump.mean()*100,1),'WAPE',[round((g.actual-pr).abs().sum()/g.actual.sum()*100,1) for pr in [g.base,g.base*g.score]])
    for floor in (100000,):
        stable = g[g.base >= floor]
        selected = stable.nlargest(round(len(stable)*.2), 'score')
        print('prior-year target month >= $100k',len(stable), 'all and selected percent',round(100*stable.jump.mean(),1),round(100*selected.jump.mean(),1))
    # Match products from China within HS4 on pre-proposal import value and momentum.
    # Exclude metal chapters and codes proposed by the decision date from the control pool.
    ctrl=d[~d.index.isin(set.union(*lists[:group+1]))]
    pairs=[]
    def features(x):return np.column_stack([np.log(x.prior),np.log1p(x.score)])
    for h,x in g.groupby('ch4'):
        if h[:2] in ('72','73','76'):continue
        c=ctrl[ctrl.ch4==h]
        if c.empty:continue
        # require base-period size within factor two and 1+growth within factor 1.25
        dist=cdist(features(x)/[np.log(2),np.log(1.25)],features(c)/[np.log(2),np.log(1.25)],metric='chebyshev')
        ix=dist.argmin(axis=1)
        for j,k in enumerate(ix):
            if dist[j,k]<=1:
                pairs.append((h,x.index[j],c.index[k],int(x.jump.iloc[j])-int(c.jump.iloc[k]),float(x.qjump.iloc[j])-float(c.qjump.iloc[k])))
    f=pd.DataFrame(pairs,columns=['h','t','c','v','q'])
    for measure in ['v','q']:
        v=f.dropna(subset=[measure])
        sums=v.groupby('h')[measure].agg(['sum','count']).values
        rng=np.random.default_rng(10)
        b=sums[rng.integers(len(sums),size=(3000,len(sums)))].sum(axis=1)
        print('matched',measure,len(v),len(sums),v.c.nunique(),'gap pp',np.round(np.r_[v[measure].mean(),np.quantile(b[:,0]/b[:,1],[.025,.975])]*100,1))
for y in (2017,2018):
    for cut,target,i in [(1,5,0),(1,6,0),(4,7,1),(5,8,2)]:
        wave(y,cut,target,i)
