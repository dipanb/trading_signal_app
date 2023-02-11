import ssl
import requests
import constants.defs as defs
import pandas as pd
from dateutil import parser
from datetime import datetime as dt

class OandaApi:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization" : f"Bearer {defs.API_KEY}",
            "Content-Type" : "application/json"
        })

    def make_request(self,url,verb='get',code = 200, params=None,data=None, headers=None):
        full_url = f"{defs.OANDA_URL}/{url}"
        try:
            response = None
            if verb=='get':
                response = self.session.get(url,params=params,data=data,headers=headers)

            if response == None:
                return False, {'error':'verb not found'}
            
            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()

        except Exception as error:
            return False, {'Exception' : 'verb not found'}

    def get_account_ep(self, ep, data_key):
        url = f"accounts/{defs.ACCOUNT_ID}/{ep}"
        ok,data = self.make_request(url)
        if ok == True and data_key in data:
            return data[data_key]
        else:
            print("ERROR get_account_ep()", data)
            return None
        
    def get_account_summary(self):
        return self.get_account_ep("summary","account")
    
    def get_account_instruments(self):
        return self.get_account_ep("instruments","instruments")
    
    def fetch_candles(self, pair_name, count=10, granularity = 'H1',
                      price ="MBA",date_f = None, date_t = None):
        url = f"instruments/{pair_name}/candles"
        params = dict(
            granularity = granularity,
            price = price
        )

        if date_f is not None and date_t is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params['from'] = dt.strftime(date_f,date_format)
            params['to'] = dt.strftime(date_t,date_format)
        else:
            params['count'] = count

        ok,data = self.make_request(url,params=params)
        if ok == True and 'candles' in data:
            return data['candles']
        else:
            print("ERROR get_account_ep()", params, data)
            return None
                
     

    def get_candle_df(self, pair_name,**kwargs):

        data = self.fetch_candles(pair_name,**kwargs)
        if data is None:
            return None
        if len(data) == 0:
            return pd.DataFrame()

        final_data = []
        prices = ['mid','bid','ask']
        ohlc = ['o','l','h','c']
        for candle in data:
            if candle['complete']==False:
                continue
            temp = {}
            temp['time'] = parser.parse(candle['time'])
            temp['volume'] = candle['volume']
            for p in prices:
                if p in candle:
                    for o in ohlc:
                        temp[f"{p}_{o}"] = float(candle[p][o])
            final_data.append(temp)
        df = pd.DataFrame.from_dict(final_data) 
        return df