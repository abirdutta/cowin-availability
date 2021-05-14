# Modified from
# https://github.com/bhattbhavesh91/cowin-vaccination-slot-availability

import datetime
import json
import numpy as np
import requests
import pandas as pd
import streamlit as st
from copy import deepcopy

# Faking chrome browser
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
df_18 = pd.DataFrame()
df_45 = pd.DataFrame()

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_mapping():
    df = pd.read_csv("./district_list.csv")
    return df

def filter_column(df, col, value):
    df_temp = deepcopy(df.loc[df[col] == value, :])
    return df_temp

def filter_capacity(df, col, value):
    df_temp = deepcopy(df.loc[df[col] > value, :])
    return df_temp

dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])


mapping_df = load_mapping()

mapping_dict = pd.Series(mapping_df["district id"].values,
                         index = mapping_df["district name"].values).to_dict()

rename_mapping = {
    'date': 'Date',
    'min_age_limit': 'Minimum Age Limit',
    'available_capacity': 'Available Capacity',
    'vaccine': 'Vaccine',
    'pincode': 'Pincode',
    'name': 'Hospital Name',
    'state_name' : 'State',
    'district_name' : 'District',
    'block_name': 'Block Name',
    'fee_type' : 'Fees'
    }

st.markdown("<h1 style='text-align: center; color: white;'>CoWin Vaccine Availability</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: yellow;'>The CoWIN APIs are geo-fenced so sometimes you may not see an output! Please try after sometime</h3>", unsafe_allow_html=True)

unique_districts = list(mapping_df["district name"].unique())
unique_districts.sort()

left_column_1, right_column_1 = st.beta_columns(2)
with right_column_1:
    numdays = st.slider('Select Date Range', 0, 100, 5)

with left_column_1:
    dist_inp = st.multiselect('Select District', unique_districts) #Changed to Multi select

DIST_ID = dictfilt(mapping_dict,dist_inp).values()

base = datetime.datetime.today()
date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
date_str = [x.strftime("%d-%m-%Y") for x in date_list]

final_df = None
for INP_DATE in date_str:
    for distid in DIST_ID: # Added a loop for District
        URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={}&date={}".format(distid, INP_DATE) #Changed to Non Public API
        response = requests.get(URL, headers=browser_header)
        if (response.ok) and ('centers' in json.loads(response.text)):
            resp_json = json.loads(response.text)['centers']
            if resp_json is not None:
                df = pd.DataFrame(resp_json)
                if len(df):
                    df = df.explode("sessions")
                    df['min_age_limit'] = df.sessions.apply(lambda x: x['min_age_limit'])
                    df['vaccine'] = df.sessions.apply(lambda x: x['vaccine'])
                    df['available_capacity'] = df.sessions.apply(lambda x: x['available_capacity'])
                    df['date'] = df.sessions.apply(lambda x: x['date'])
                    df = df[["date", "available_capacity", "vaccine", "min_age_limit", "pincode", "name", "state_name", "district_name", "block_name", "fee_type"]]
                    if final_df is not None:
                        final_df = pd.concat([final_df, df])
                    else:
                        final_df = deepcopy(df)
            else:
                st.error("No rows in the data Extracted from the API")

if len(DIST_ID):
    if (final_df is not None) and (len(final_df)):
        final_df.drop_duplicates(inplace=True)
        final_df.rename(columns=rename_mapping, inplace=True)

        center_column_2a, center_column_2b = st.beta_columns(2)

        with center_column_2a:
            option_18 = st.checkbox('18+')
        with center_column_2b:
            option_45 = st.checkbox('45+')
            
        if option_18:
            df_18 = filter_column(final_df, "Minimum Age Limit", 18)
        if option_45:
            df_45 = filter_column(final_df, "Minimum Age Limit", 45)
        if (option_18) or (option_45):
            final_df = pd.concat([df_18,df_45])

        right_column_2, right_column_2a,  right_column_2b = st.beta_columns(3)

        with right_column_2:
            valid_payments = ["Free", "Paid"]
            pay_inp = st.selectbox('Select Free or Paid', [""] + valid_payments)
            if pay_inp != "":
                final_df = filter_column(final_df, "Fees", pay_inp)

        with right_column_2a:
            valid_capacity = ["Available"]
            cap_inp = st.selectbox('Select Availablilty', [""] + valid_capacity)
            if cap_inp != "":
                final_df = filter_capacity(final_df, "Available Capacity", 0)

        with right_column_2b:
            valid_vaccines = ["COVISHIELD", "COVAXIN"]
            vaccine_inp = st.selectbox('Select Vaccine', [""] + valid_vaccines)
            if vaccine_inp != "":
                final_df = filter_column(final_df, "Vaccine", vaccine_inp)

        table = deepcopy(final_df)
        table.reset_index(inplace=True, drop=True)
        st.table(table)
    else:
        st.error("Unable to fetch data currently, please try after sometime")
