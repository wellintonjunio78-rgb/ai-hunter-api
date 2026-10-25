import os, time, threading
from datetime import datetime, timezone
from pathlib import Path
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ml_core import features, FEATURES

app=FastAPI(title='AI Hunter research API',version='1.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['GET'],allow_headers=['*'])
SYMBOLS=['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','TRXUSDT','DOTUSDT']
_cache={'at':0,'data':None}; lock=threading.Lock(); model_bundle=None; model_error=None

def load_model():
    global model_bundle,model_error
    if model_bundle is not None: return model_bundle
    if os.getenv('TRUST_MODEL_FILE')!='yes':
        model_error='Model loading disabled: set TRUST_MODEL_FILE=yes only if you trust the uploaded joblib file.'
        return None
    try:
        import joblib
        model_bundle=joblib.load(Path(__file__).parent/'model_v3.joblib')
        if model_bundle.get('features')!=FEATURES: raise ValueError('Feature order mismatch')
    except Exception as e: model_error=f'{type(e).__name__}: {e}';model_bundle=None
    return model_bundle

@app.get('/health')
def health():
    b=load_model()
    return {'status':'ok','model_loaded':b is not None,'model_error':model_error,'mode':'research_only'}

def get_one(s,bundle):
    response=requests.get('https://data-api.binance.vision/api/v3/klines',params={'symbol':s,'interval':'1m','limit':130},timeout=12)
    response.raise_for_status();rows=response.json(); now=int(time.time()*1000)
    rows=[r for r in rows if int(r[6])<now]
    if len(rows)<70: raise ValueError('Insufficient closed candles')
    x=features(rows).iloc[[-1]][FEATURES]
    if x.isna().any().any(): raise ValueError('Missing features')
    p=float(bundle['model'].predict_proba(x)[0][list(bundle['model'].classes_).index(1)])
    report=bundle.get('report',{})
    return {'symbol':s,'price':float(rows[-1][4]),'last_closed_ms':int(rows[-1][6]),'probability_research':round(p,5),'decision':'AGUARDAR','validated':False,'horizon_minutes':report.get('horizon_minutes',5)}

@app.get('/scan')
def scan():
    b=load_model()
    if b is None:raise HTTPException(status_code=503,detail=model_error or 'Model unavailable')
    with lock:
        if _cache['data'] is not None and time.time()-_cache['at']<25:return _cache['data']
        items=[];errors={}
        for s in SYMBOLS:
            try:items.append(get_one(s,b))
            except Exception as e:errors[s]=str(e)[:180]
        items.sort(key=lambda v:v['probability_research'],reverse=True)
        result={'timestamp':datetime.now(timezone.utc).isoformat(),'model':'V3','mode':'RESEARCH_ONLY','signal_status':b.get('report',{}).get('signal_status','UNKNOWN'),'items':items,'errors':errors,'notice':'Scores are uncalibrated research estimates, not trading probabilities or buy/sell signals.'}
        if not items:raise HTTPException(status_code=502,detail={'message':'Binance data unavailable','errors':errors})
        _cache.update(at=time.time(),data=result)
        return result
