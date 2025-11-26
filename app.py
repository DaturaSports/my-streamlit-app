import streamlit as st

# Minimal UI
st.title("Betting Tool")
st.write("EV Calculator")

prob = st.number_input("Win Probability", 0.0, 1.0, 0.6)
odds = st.number_input("Decimal Odds", 1.01, 100.0, 2.0)

ev = prob - (1 / odds)
st.write(f"EV: {ev:.3f}")

if ev > 0:
    stake = 0.5 * ev / (1 - prob)
    st.write(f"Stake: {stake:.1%}")
else:
    st.write("No bet")
