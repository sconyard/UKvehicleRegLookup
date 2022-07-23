import requests
from requests.structures import CaseInsensitiveDict
from pandas.io.json import json_normalize
import pandas as pd
import streamlit as st
from streamlit_tags import st_tags

# multiple vehicle lookup function
def car_regs_lookup():
# build empty dataframe
    multicar_reg = pd.DataFrame()

# for loop to iterate through the list of registration numbers
    for x in regs: 
        try:
# base url for the API
            url = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

# URL headers
            headers = CaseInsensitiveDict()
            headers["x-api-key"] = "Your API KEY"
            headers["Content-Type"] = "application/json"

# API data request the format requires the passing of {} and "" as strings hence the formatting options
            data = str({"registrationNumber": str(x)}).replace("'", '"')

# API request
            resp = requests.post(url, headers=headers, data=data)

# Write out the API status code
            st.markdown(f'<h1 style="color:#6ac94f;font-size:12px;">returned API Status Code = {resp.status_code}</h1>', unsafe_allow_html=True)

# If the API status code is not 200 then raise an exception   
            if resp.status_code != 200:
                raise Exception("Error: {}".format(resp.status_code))
            else:
# Write out the API response
                st.write(resp.json())

# Convert the API response to a pandas dataframe
                json = resp.json()
                car_reg = json_normalize(json)

# Append the response dataframe to the empty dataframe
                multicar_reg = pd.concat([multicar_reg, car_reg])
        except:
# If an exception is raised then write out the error message
            st.warning("No data found for provided registration number, please try again")

# Write out the merged dataframe
    st.dataframe(multicar_reg)

# Convert the dataframe to a CSV
    def convert_df(multicar_reg):
        return multicar_reg.to_csv().encode('utf-8')
    csv = convert_df(multicar_reg)

# Create a download button for the CSV
    st.download_button(
        label="Download Output as CSV",
        data=csv,
        file_name=(f'CarDetails.csv'),
        mime='text/csv',
        )

# Single vehicle lookup function  
def car_reg_lookup():
    try:
# Write out the caputred registration number
        st.write(st.session_state.reg)

# base url for the API
        url = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

# URL headers
        headers = CaseInsensitiveDict()
        headers["x-api-key"] = "Your API Key"
        headers["Content-Type"] = "application/json"

# API data request the format requires the passing of {} and "" as strings hence the formatting options
        data = str({"registrationNumber": str(st.session_state.reg)}).replace("'", '"')

# API request
        resp = requests.post(url, headers=headers, data=data)

# Write out the API status code
        st.markdown(f'<h1 style="color:#6ac94f;font-size:12px;">returned API Status Code = {resp.status_code}</h1>', unsafe_allow_html=True)

# If the API status code is not 200 then raise an exception
        if resp.status_code != 200:
            raise Exception("Error: {}".format(resp.status_code))
        else:

# Write out the API response
            st.write(resp.json())

# Convert the API response to a pandas dataframe
            json = resp.json()
            car_reg = json_normalize(json)

# Write out the dataframe
            st.dataframe(car_reg)

# Convert the dataframe to a CSV
            def convert_df(car_reg):
                return car_reg.to_csv().encode('utf-8')
            csv = convert_df(car_reg)

# Create a download button for the CSV
            st.download_button(
                label="Download Output as CSV",
                data=csv,
                file_name=(f'CarDetails{st.session_state.reg}.csv'),
                mime='text/csv',
                )
    except:
# If an exception is raised then write out the error message
        st.warning("No data found for provided registration number, please try again")

# This section creates managed the look and feel of the interface displays reference information
st.set_page_config(
   layout="wide", page_title="UK DVLA API - Car Registration Lookup")

st.title("UK DVLA API - Car Registration Lookup")
st.markdown("This tool can be used to lookup a vehicle registration number and return the details of the vehicle.")
st.markdown("Information about the API is available from this [DVLA website](https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html#vehicle-enquiry-service-api)")

# This section is the text input for the single registration lookup
reg = st.text_input("Vehicle Registration to Lookup", "EXAMPLE", key="reg")

# This section is the text input for the multiple registration lookup
regs = st_tags(label="Input Multiple Vehicle Registrations",
               text="Press enter to add more",
               key="regs",)     

# This section is the button for the single registration lookup
if st.button('Perform single vehicle lookup'):
    car_reg_lookup() 

# This section is the button for the multiple registration lookup
if st.button('Perform multiple vehicle lookup'):
    car_regs_lookup()
