"""Settings page: opening cash and balance-sheet figures."""
import math

import streamlit as st

from database import crud
from utils.file_processing import _to_number

FIELDS = [
    ("opening_cash", "Opening cash + bank balance",
     "Money you had BEFORE your first recorded transaction. Used for Cash Flow.", True),
    ("current_assets", "Current assets",
     "Cash, bank, money customers owe you, and stock value. Used for the Current Ratio.", False),
    ("current_liabilities", "Current liabilities",
     "Bills and loans due within 12 months (e.g. supplier balances). Used for the Current Ratio.", False),
]


def render() -> None:
    st.title("⚙️ Settings")
    st.subheader("Opening balances and balance-sheet figures (optional)")
    st.caption("Leave a field empty if you don't know it. The app will say 'insufficient data' "
               "instead of guessing.")
    current = crud.get_numeric_settings()

    with st.form("settings_form"):
        entered = {}
        for key, label, help_text, _ in FIELDS:
            saved = current.get(key)
            entered[key] = st.text_input(f"{label} ({st.session_state.profile['currency']})",
                                         value="" if saved is None else f"{saved:.0f}",
                                         help=help_text)
        submitted = st.form_submit_button("Save settings")

    if not submitted:
        return

    parsed, errors = {}, []
    for key, label, _, allow_negative in FIELDS:
        text = entered[key].strip()
        if text == "":
            parsed[key] = None
            continue
        number = _to_number(text)
        if isinstance(number, float) and math.isnan(number):
            errors.append(f"{label}: '{text}' is not a valid number.")
        elif number < 0 and not allow_negative:
            errors.append(f"{label} cannot be negative.")
        else:
            parsed[key] = number
    if errors:
        for message in errors:
            st.error(message)
        return
    for key, value in parsed.items():
        crud.set_numeric_setting(key, value)
    st.success("Settings saved.")
