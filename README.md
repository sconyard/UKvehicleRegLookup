# UK Vehicle Lookup from Registration

Simple application to demonstrate looking up values from an API.

Application uses Python, with Streamlit, Streamlit_tags, Pandas, Requests and the [UK Vehicle Enquiry Service API](https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html#vehicle-enquiry-service-api)

## How does it work

Using [Streamlit](https://streamlit.io/) makes it easier to build something usable in a few minutes.

Streamlit provides the layout, text inputs, buttons and streamlit_tags provides the list input box.

![First Launch](https://github.com/sconyard/UKvehicleRegLookup/blob/ffa051cd1ac3d20e6f8ed03554ec19911d200175/images/FirstLaunch.png)

The buttons link to functions that perform either a single vehicle registration lookup against the DVLA vehicle API or interate over a list provided from the list inputs.

The text input for the single vehicle registration includes a session_state element (key) that is passed to Requests (st.session_state.reg) and included in the query string for the API lookup. 

![Single Query](https://github.com/sconyard/UKvehicleRegLookup/blob/0f617696e4ba557604b5247ef4749766639ef1ff/images/SingleResponse.png)

The json response is flattend and passed into a pandas dataframe for display.

A function button to export the dataframe as a csv file is also included.

For the multi vehicle lookup a list is gathered using the [streamlit_tags](https://streamlit-tags.readthedocs.io/en/latest/) capturing a session state as per the single lookup will not work for the list, so the list is captured as a variable (regs) and passed to a for x in regs loop.

The API query data is changed to use the value of x from regs.  Each json response is flattened and pd.concat used to append the data to a dataframe built outside the loop.

![Multiple Queries](https://github.com/sconyard/UKvehicleRegLookup/blob/0f617696e4ba557604b5247ef4749766639ef1ff/images/MultiResponse.png)

As before a function button to export the appended dataframe as a csv is also provided.

## Error Handling

Error handling is provided by reviwing the API response code.  If the response is not equal to 200 then an exception is triggered. A response code other thatn 200 will most likley been recieved when the vehicle registration entered is incorrect, the exception assumes this in the response.  The returned API code is also written to aide troubleshooting if required.

![Exception](https://github.com/sconyard/UKvehicleRegLookup/blob/0f617696e4ba557604b5247ef4749766639ef1ff/images/SingleError.png)

### Support

No support offered or liability accepted use is entirely at your own risk.

