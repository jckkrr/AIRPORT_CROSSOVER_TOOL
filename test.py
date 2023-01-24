### streamlit run "C:\Users\Jack\Documents\Python_projects\aviation\aviation_tools\test.py"

#from bs4 import BeautifulSoup
import datetime
import json
import pandas as pd
import os
from requests import get
import re
import requests
import streamlit as st

####

def scrapingTools_getSoup(url):
    
    ### this originally used bs4, but that wouln't deploy, so this has been altered slightly but kept the 'soup' name
    
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    headers = {'User-Agent': user_agent,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    response = get(url, headers=headers)
    
    soup = response.content.decode('ASCII')
        
    return soup

def timeFuncs_returnEpoch(YYYYmmdd):
   
    epochTime = int(datetime.datetime.strptime(str(YYYYmmdd), "%Y%m%d").timestamp())
    
    return epochTime

def hexdbioTools_convertIATAtoICAO(IATA):
    
    url = f'https://hexdb.io/iata-icao?iata={IATA}'    
    ICAO_AIRPORT = scrapingTools_getSoup(url)
    
    return ICAO_AIRPORT

    
def hexdbioTools_airportInfo(ICAO_AIRPORT):
    
    url = f'https://hexdb.io/api/v1/airport/icao/{ICAO_AIRPORT}'        
    soup = scrapingTools_getSoup(url)    
    jl = json.loads(soup)
    df = pd.DataFrame.from_dict(jl, orient="index").T
    
    return df

def hexdbioTools_aircraftInfo(ICAOHEX, getImageUrl):
        
    url = f'https://hexdb.io/api/v1/aircraft/{ICAOHEX}'
    soup = scrapingTools_getSoup(url)
    jl = json.loads(soup)
    df = pd.DataFrame.from_dict(jl, orient="index").T
    
    if getImageUrl == True:                          ## this can take a while for some reason
        df['image_url'] = imageRetrieval(ICAOHEX)
    
    return df

def hexdbioTools_aicraftInfo_multi(list_of_icaohex):
    
    df = pd.DataFrame()
    for icaohex in list_of_icaohex:
        dfx = hexdbioTools_aircraftInfo(icaohex, False)
        dfx['icaohex'] = icaohex
        df = pd.concat([df,dfx])
        
    df = df.reset_index(drop=True)
    
    return df 
    
def openskyTools_getBasicDailyAirportArriveOrDepart(dayYYYYmmdd, airportIcao, arrival_or_departure):
    
    df = pd.DataFrame()
    
    st.write(ICAO_AIRPORT)
        
    dayEpoch = timeFuncs_returnEpoch(dayYYYYmmdd)
    dateddmm = f'{str(dayYYYYmmdd)[6:8]}/{str(dayYYYYmmdd)[4:6]}/{str(dayYYYYmmdd)[0:4]}'
    
    st.write(dateddmm, end='\t\t')
    
    st.write('Accessing API data. ', end=' ')
    url = f'https://opensky-network.org/api/flights/{arrival_or_departure}?airport={airportIcao}&begin={dayEpoch}&end={dayEpoch+86400}'
    response = requests.request("GET", url) 
    
    if response.status_code != 200:
        print(response)
    
    j = response.json()    
    st.write(f'{len(j)} entries: ', end='')
    
    for i in j:
        
        st.write('.', end='')
        
        df.loc[j.index(i), ['Date', 'Date Epoch']] = [dayYYYYmmdd, dayEpoch] 
        
        for key, val in i.items():
            if type(val) == str:
                val = val.strip()
            df.loc[j.index(i), key] = val
                        
        df.loc[j.index(i), 'Source'] = 'OpenSky Network'
        
    df = df.rename(columns={'estDepartureAirport': 'originIcao', 'estArrivalAirport': 'destinationIcao'})
    
    return df

####



#### MAIN FUNCTION

def comparePlanesDayArrDep(arrive_yyyymmdd, depart_yyyymmdd, IATA_AIRPORT_CODE):
    
    ## most people will use a three digit airport code, not the four letter ICAO code, so first job is to covert
    ICAO_AIRPORT = hexdbioTools_convertIATAtoICAO(IATA_AIRPORT_CODE)
    
    st.write(ICAO_AIRPORT)
    
    # get daily arrival/depart data
    arrivals = openskyTools_getBasicDailyAirportArriveOrDepart(arrive_yyyymmdd, ICAO_AIRPORT, 'arrival')
    arrivals = arrivals.loc[arrivals['originIcao'] != arrivals['destinationIcao']]  ## to exclude helicopters doing joy flights, for example
    
    st.DataFrame(arrivals)
    
    departures = openskyTools_getBasicDailyAirportArriveOrDepart(depart_yyyymmdd, ICAO_AIRPORT, 'departure')
    departures = departures.loc[departures['originIcao'] != departures['destinationIcao']]
        
    callsigns_arr = arrivals['callsign'].to_list()
    callsigns_dep = departures['callsign'].to_list()
    crossover_aircraft = [x for x in callsigns_arr if x in callsigns_dep]
    print(crossover_aircraft)    
    icao_hex_codes = [x for x in departures.loc[departures['callsign'].isin(crossover_aircraft), 'icao24'].unique()]
    
    dfARRMINI = arrivals.loc[arrivals['callsign'].isin(crossover_aircraft), ['callsign', 'icao24', 'Date', 'originIcao', 'lastSeen']].rename(columns={'Date': 'arrive_date', 'originIcao': 'arrived_from'})
    
    
    dfDEPMINI = departures.loc[departures['callsign'].isin(crossover_aircraft), ['callsign', 'icao24', 'Date', 'destinationIcao', 'firstSeen', ]].rename(columns={'Date': 'depart_date', 'destinationIcao': 'departed_for'})  
        
    ### Get deatils about where they are coming from or going to
    def getOtherAirportInfo(df, ARR_or_DEP):

        col = 'arrived_from' if ARR_or_DEP == 'ARR' else 'departed_for' if ARR_or_DEP == 'DEP' else None

        dfOTHERAIRPORTS = pd.DataFrame()
        for other_airport in df[col].unique():
                    
            dfx = hexdbioTools_airportInfo(other_airport)
                        
            if f'{ARR_or_DEP}_icao' not in dfx.columns:
                dfx['icao'] = other_airport
            
            dfOTHERAIRPORTS = pd.concat([dfOTHERAIRPORTS, dfx])

        dfOTHERAIRPORTS = dfOTHERAIRPORTS.reset_index(drop=True)
        dfOTHERAIRPORTS.columns = [f'{ARR_or_DEP}_{x}' for x in dfOTHERAIRPORTS.columns]

        df = df.merge(dfOTHERAIRPORTS, left_on=col, right_on=f'{ARR_or_DEP}_icao')

        return df

    dfARRMINI = getOtherAirportInfo(dfARRMINI, 'ARR')
    dfDEPMINI = getOtherAirportInfo(dfDEPMINI, 'DEP')
    
    dfMINI = dfARRMINI.merge(dfDEPMINI, on = ['callsign', 'icao24']).rename(columns={'icao24': 'icaohex'})
              
        
    ### Get info about aircraft     
    dfAIRCRAFTINFO = hexdbioTools_aicraftInfo_multi(icao_hex_codes)
    
    df = dfAIRCRAFTINFO.merge(dfMINI, on = ['icaohex'])
    
    df['central_airport_icao'] = ICAO_AIRPORT
    
    order_cols = ['Registration', 'icaohex', 'RegisteredOwners', 'Manufacturer', 'Type', 'arrived_from', 'ARR_airport', 'ARR_country_code', 'departed_for', 'DEP_airport', 'DEP_country_code', 'ARR_iata', 'DEP_iata', 'arrive_date', 'lastSeen', 'depart_date', 'firstSeen', 'ARR_latitude', 'ARR_longitude', 'ARR_region_name', 'DEP_latitude', 'DEP_longitude', 'DEP_region_name', 'OperatorFlagCode', 'ICAOTypeCode', 'central_airport_icao']
    display_cols = [x for x in order_cols if x in df.columns]
        
    df = df[display_cols]

    return df


############################# RUN #############################

IATA_AIRPORT_CODE = st.text_input('Please enter the 3-letter IATA code for the aiport you are interested in: ', 'BQH')
ICAO_AIRPORT_CODE = hexdbioTools_convertIATAtoICAO(IATA_AIRPORT_CODE)

st.write(ICAO_AIRPORT_CODE)

start_date = st.date_input('Start date', datetime.datetime(2022, 11, 3, 0, 0, 0))
end_date = st.date_input('End date', datetime.datetime(2022, 11, 7, 0, 0, 0))
if start_date < end_date:
    st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.error('Error: End date must fall after start date.')

proceed = st.radio('Ready to go?', ['no','yes'], horizontal=True)

if proceed == 'yes':
    
    st.write('Getting data ...')
    
    
    df = comparePlanesDayArrDep(20221103, 20221107, 'BQH')
    
    st.dataframe(df)
    
    
st.write('')
st.write('')
st.write('&#11041; More tools at www.constituent.au')