# UK Vehicle Lookup from Registration

Simple application to demonstrate looking up values from an API.

Application uses Python, with Streamlit, Streamlit_tags, Pandas and Requests

## How does it work

Using [Streamlit](https://streamlit.io/) makes it easier to build something usable in a few minutes.

Streamlit provides the layout, text inputs, buttons and streamlit_tags provides the list input box.

![First Launch](https://github.com/sconyard/UKvehicleRegLookup/blob/ffa051cd1ac3d20e6f8ed03554ec19911d200175/images/FirstLaunch.png)

The buttons link to functions that perform either a single vehicle registration lookup against the DVLA vehicle API or interate over a list provided from the list inputs.

The text input for the single vehicle registration includes a session_state element (key) that is passed to Requests (st.session_state.reg) and included in the query string for the API lookup. 

![Single Query](https://github.com/sconyard/UKvehicleRegLookup/blob/0f617696e4ba557604b5247ef4749766639ef1ff/images/SingleResponse.png)
