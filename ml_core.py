import numpy as np
import pandas as pd

FEATURES=['ret1','ret3','ret5','range','body','vol_ratio','ema_gap','ema_slope','rsi','volatility','hour_sin','hour_cos']

def features(rows):
    df=pd.DataFrame(rows,columns=['open_time','open','high','low','close','volume','close_time','quote_volume','trades','taker_base','taker_quote','ignore'])
    for col in ['open','high','low','close','volume']: df[col]=pd.to_numeric(df[col])
    c=df.close; ret=c.pct_change(); e9=c.ewm(span=9,adjust=False).mean(); e21=c.ewm(span=21,adjust=False).mean()
    delta=c.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    rsi=100-100/(1+gain/loss.replace(0,np.nan)); rsi=rsi.fillna(50)
    hour=pd.to_datetime(df.open_time,unit='ms',utc=True).dt.hour
    x=pd.DataFrame({'ret1':ret,'ret3':c.pct_change(3),'ret5':c.pct_change(5),'range':(df.high-df.low)/c,'body':(c-df.open)/c,'vol_ratio':df.volume/df.volume.rolling(20).mean(),'ema_gap':(e9-e21)/c,'ema_slope':e9.pct_change(3),'rsi':rsi/100,'volatility':ret.rolling(20).std(),'hour_sin':np.sin(2*np.pi*hour/24),'hour_cos':np.cos(2*np.pi*hour/24)})
    return x.replace([np.inf,-np.inf],np.nan)

def labels(rows,threshold=0.001):
    close=np.array([float(r[4]) for r in rows]); forward=np.r_[close[1:]/close[:-1]-1,np.nan]
    return pd.Series(np.where(forward>threshold,1,np.where(forward < -threshold,-1,0)),dtype='float64').mask(np.isnan(forward))
