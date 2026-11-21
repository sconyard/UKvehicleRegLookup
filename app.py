"""Streamlit front end for the DVLA Vehicle Enquiry Service API."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from dvla import LIVE_URL, UAT_URL, LookupResult, VehicleEnquiryClient, parse_reg_list

MAX_BATCH = 100  # keep accidental huge pastes from hammering the API

# Fields shown first in tables, in a sensible order. Any other fields follow.
PREFERRED_COLUMNS = [
    "registrationNumber",
    "make",
    "colour",
    "yearOfManufacture",
    "monthOfFirstRegistration",
    "fuelType",
    "engineCapacity",
    "co2Emissions",
    "taxStatus",
    "taxDueDate",
    "motStatus",
    "motExpiryDate",
    "markedForExport",
    "wheelplan",
    "typeApproval",
    "euroStatus",
    "dateOfLastV5CIssued",
]


def configured_api_key() -> str:
    """API key from Streamlit secrets or the DVLA_API_KEY environment variable."""
    try:
        key = st.secrets.get("DVLA_API_KEY", "")
    except Exception:  # no secrets.toml present - exception type varies by Streamlit version
        key = ""
    return key or os.environ.get("DVLA_API_KEY", "")


@st.cache_data(ttl=3600, show_spinner=False)
def cached_lookup(reg: str, url: str, _api_key: str) -> LookupResult:
    # _api_key is excluded from the cache hash so the key never ends up in cache metadata.
    return VehicleEnquiryClient(_api_key, url=url).lookup(reg)


def to_dataframe(results: list[LookupResult]) -> pd.DataFrame:
    df = pd.json_normalize([r.data for r in results if r.ok])
    if df.empty:
        return df
    ordered = [c for c in PREFERRED_COLUMNS if c in df.columns]
    return df[ordered + [c for c in df.columns if c not in ordered]]


def errors_dataframe(results: list[LookupResult]) -> pd.DataFrame:
    df = pd.DataFrame(
        [{"registration": r.registration, "status": r.status_code, "error": r.error} for r in results if not r.ok]
    )
    if not df.empty:
        df["status"] = df["status"].astype("Int64")
    return df


def run_lookups(regs: list[str], url: str, api_key: str) -> list[LookupResult]:
    results = []
    progress = st.progress(0.0, text="Looking up vehicles...") if len(regs) > 1 else None
    for i, reg in enumerate(regs, start=1):
        results.append(cached_lookup(reg, url, api_key))
        if progress:
            progress.progress(i / len(regs), text=f"Looked up {i} of {len(regs)}")
    if progress:
        progress.empty()
    return results


def show_single(result: LookupResult) -> None:
    if not result.ok:
        st.error(f"**{result.registration}**: {result.error}")
        return
    d = result.data
    st.subheader(f"{d.get('registrationNumber', result.registration)} - {d.get('make', 'Unknown make')}")
    cols = st.columns(4)
    cols[0].metric("Colour", str(d.get("colour", "-")).title())
    cols[1].metric("Year", d.get("yearOfManufacture", "-"))
    cols[2].metric("Tax", d.get("taxStatus", "-"), help=f"Due: {d.get('taxDueDate', 'n/a')}")
    cols[3].metric("MOT", d.get("motStatus", "-"), help=f"Expires: {d.get('motExpiryDate', 'n/a')}")
    if d.get("markedForExport"):
        st.warning("This vehicle is marked for export.")
    with st.expander("All returned fields"):
        st.dataframe(to_dataframe([result]).T.astype(str).rename(columns={0: "value"}), width="stretch")
    with st.expander("Raw JSON"):
        st.json(d)


def show_results(results: list[LookupResult]) -> None:
    if len(results) == 1:
        show_single(results[0])
    else:
        found = sum(r.ok for r in results)
        st.subheader(f"Found {found} of {len(results)} vehicles")
        df = to_dataframe(results)
        if not df.empty:
            st.dataframe(df, width="stretch", hide_index=True)
        errors = errors_dataframe(results)
        if not errors.empty:
            st.markdown("**Not found / errors**")
            st.dataframe(errors, width="stretch", hide_index=True)

    df = to_dataframe(results)
    if not df.empty:
        name = f"VehicleDetails_{results[0].registration}.csv" if len(results) == 1 else "VehicleDetails.csv"
        st.download_button(
            "Download results as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=name,
            mime="text/csv",
        )


# ---------------------------------------------------------------- page layout
st.set_page_config(layout="wide", page_title="UK DVLA Vehicle Lookup", page_icon=":car:")
st.title("UK DVLA Vehicle Lookup")
st.markdown(
    "Look up one or more UK vehicle registrations using the DVLA "
    "[Vehicle Enquiry Service API](https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/"
    "vehicle-enquiry-service/vehicle-enquiry-service-description.html)."
)

with st.sidebar:
    st.header("Settings")
    api_key = configured_api_key()
    if api_key:
        st.success("API key loaded from configuration.")
    else:
        api_key = st.text_input(
            "DVLA API key",
            type="password",
            help="Set DVLA_API_KEY in .streamlit/secrets.toml or the environment to skip this.",
        )
    use_uat = st.toggle("Use UAT (test) environment", help="UAT keys only work against the UAT endpoint.")
    api_url = UAT_URL if use_uat else LIVE_URL
    if st.button("Clear cached results"):
        cached_lookup.clear()
        st.session_state.pop("results", None)

if not api_key:
    st.info("Enter your DVLA API key in the sidebar to get started.")
    st.stop()

single_tab, multi_tab = st.tabs(["Single lookup", "Multiple lookup"])

with single_tab:
    with st.form("single"):
        reg = st.text_input("Vehicle registration", placeholder="e.g. AB12 CDE", max_chars=10)
        if st.form_submit_button("Look up vehicle", type="primary"):
            regs = parse_reg_list(reg)
            if regs:
                st.session_state.results = run_lookups(regs[:1], api_url, api_key)
            else:
                st.warning("Enter a registration number.")

with multi_tab:
    with st.form("multi"):
        text = st.text_area(
            "Vehicle registrations",
            placeholder="One per line, or comma separated",
            height=150,
        )
        upload = st.file_uploader("...or upload a .txt / .csv file", type=["txt", "csv"])
        if st.form_submit_button("Look up vehicles", type="primary"):
            if upload is not None:
                text = f"{text}\n{upload.getvalue().decode('utf-8', errors='ignore')}"
            regs = parse_reg_list(text)
            if not regs:
                st.warning("Enter at least one registration number.")
            else:
                if len(regs) > MAX_BATCH:
                    st.warning(f"Only the first {MAX_BATCH} of {len(regs)} registrations will be looked up.")
                    regs = regs[:MAX_BATCH]
                st.session_state.results = run_lookups(regs, api_url, api_key)

# Results live in session state so they survive reruns (e.g. clicking the download button).
if st.session_state.get("results"):
    st.divider()
    show_results(st.session_state.results)
