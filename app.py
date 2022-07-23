import requests
from requests.structures import CaseInsensitiveDict
from pandas.io.json import json_normalize
import pandas as pd
import streamlit as st
from streamlit_tags import st_tags

def car_regs_lookup():
    multicar_reg = pd.DataFrame()

    for x in regs: 
        try:
            url = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

            headers = CaseInsensitiveDict()
            headers["x-api-key"] = "YOUR API KEY"
            headers["Content-Type"] = "application/json"
            data = str({"registrationNumber": str(x)}).replace("'", '"')

            resp = requests.post(url, headers=headers, data=data)

            st.markdown(f'<h1 style="color:#6ac94f;font-size:12px;">returned API Status Code = {resp.status_code}</h1>', unsafe_allow_html=True)
            
            if resp.status_code != 200:
                raise Exception("Error: {}".format(resp.status_code))
            else:
                st.write(resp.json())

                json = resp.json()
                car_reg = json_normalize(json)

                multicar_reg = pd.concat([multicar_reg, car_reg])

        except:
            st.warning("No data found for provided registration number, please try again")

    st.dataframe(multicar_reg)

    def convert_df(multicar_reg):
        return multicar_reg.to_csv().encode('utf-8')

    csv = convert_df(multicar_reg)

    st.download_button(
        label="Download Output as CSV",
        data=csv,
        file_name=(f'CarDetails.csv'),
        mime='text/csv',
        )

def car_reg_lookup():
    try:
        st.write(st.session_state.reg)
        url = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

        headers = CaseInsensitiveDict()
        headers["x-api-key"] = "YOUR API KEY"
        headers["Content-Type"] = "application/json"
        data = str({"registrationNumber": str(st.session_state.reg)}).replace("'", '"')

        resp = requests.post(url, headers=headers, data=data)

        st.markdown(f'<h1 style="color:#6ac94f;font-size:12px;">returned API Status Code = {resp.status_code}</h1>', unsafe_allow_html=True)
        
        if resp.status_code != 200:
            raise Exception("Error: {}".format(resp.status_code))
        else:
            st.write(resp.json())

            json = resp.json()
            car_reg = json_normalize(json)

            st.dataframe(car_reg)

            def convert_df(car_reg):
                return car_reg.to_csv().encode('utf-8')
        
            csv = convert_df(car_reg)

            st.download_button(
                label="Download Output as CSV",
                data=csv,
                file_name=(f'CarDetails{st.session_state.reg}.csv'),
                mime='text/csv',
                )
    except:
        st.warning("No data found for provided registration number, please try again")

st.set_page_config(
   layout="wide", page_title="UK DVLA API - Car Registration Lookup")

st.title("UK DVLA API - Car Registration Lookup")

st.markdown("This tool can be used to lookup a vehicle registration number and return the details of the vehicle.")

st.markdown("Information about the API is available from this [DVLA website](https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html#vehicle-enquiry-service-api)")

reg = st.text_input("Vehicle Registration to Lookup", "EXAMPLE", key="reg")

if st.button('Perform single vehicle lookup'):
    car_reg_lookup()

regs = st_tags(label="Input Multiple Vehicle Registrations",
               text="Press enter to add more",
               key="regs",)      

if st.button('Perform multiple vehicle lookup'):
    car_regs_lookup()
