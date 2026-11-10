"""Surge events and whether they reverse. Trailing-only baseline (no leakage).

expected(t) = trailing 12m geometric mean x month-of-year factor estimated
from months strictly before t. Surge episode = contiguous run above 0.5 SD
that peaks above K SD. reversal = -(excess over the H months AFTER the
episode) / (excess DURING it), so both sides are cumulative and comparable.
"""
import pandas as pd, numpy as np
import warnings; warnings.filterwarnings("ignore")
K=2.0; H=9; WARM=36

df=pd.read_csv("panel/imports_hs2_panel.csv",dtype={"chapter":str,"cty_name":str})
df["date"]=pd.to_datetime(dict(year=df.year,month=df.month,day=1))
df["kg"]=df.air_kg+df.ves_kg
g=df.groupby(["chapter","cty_name","date"])["kg"].sum().reset_index()

ev=[]; cells=0
for (ch,cty),d in g.groupby(["chapter","cty_name"]):
    s=d.set_index("date")["kg"].asfreq("MS").replace(0,np.nan)
    if s.notna().sum()<WARM+H+24: continue
    s=s.interpolate(limit_area="inside").dropna()
    if len(s)<WARM+H+24: continue
    ln=np.log(s); n=len(ln); m=ln.index.month.values
    an=np.full(n,np.nan)
    for i in range(WARM,n):
        hist=ln.values[:i]; hm=m[:i]
        lvl=hist[-12:].mean()
        same=hist[hm==m[i]]
        fac=(same[-4:]-np.array([hist[max(0,j-6):j+6].mean()
              for j in np.where(hm==m[i])[0][-4:]])).mean() if (hm==m[i]).sum()>=3 else 0.0
        an[i]=ln.values[i]-(lvl+fac)
    a=pd.Series(an,index=ln.index).dropna()
    if len(a)<H+24: continue
    sd=a.iloc[:24].std(ddof=1)
    if not np.isfinite(sd) or sd<=0: continue
    cells+=1
    v=a.values; idx=a.index; i=24
    while i<len(v)-H:
        if v[i]>K*sd:
            j=i
            while j+1<len(v) and v[j+1]>0.5*sd: j+=1
            during=v[i:j+1].sum()
            after=v[j+1:j+1+H].sum()
            if during>0:
                ev.append((ch,cty,idx[i],float(during),float(-after/during)))
            i=j+H+1
        else: i+=1
e=pd.DataFrame(ev,columns=["chapter","partner","date","excess_ln","reversal"])
e.to_csv("panel/surge_events.csv",index=False)
print(f"cells modelled  : {cells:,}")
print(f"surge episodes  : {len(e):,}   (peak > {K} SD)")
r=e.reversal
print("\nreversal ratio (1.0 = fully given back, 0 = fully durable):")
for q in (10,25,50,75,90): print(f"  p{q:<3}{np.percentile(r,q):+7.2f}")
b=(r>0.6).mean()*100; m_=(r<0.2).mean()*100
print(f"\n  borrow    (>0.6 given back) : {b:.0f}%")
print(f"  boom      (<0.2 given back) : {m_:.0f}%")
print(f"  in-between                  : {100-b-m_:.0f}%")
tw=e[(e.date>="2025-01-01")&(e.date<="2025-06-30")]
print(f"\nepisodes starting in the 2025 tariff window: {len(tw):,}")
