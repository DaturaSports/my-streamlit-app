import streamlit as st
import pandas as pd

# Theme state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# CSS for UI
if st.session_state.theme == 'dark':
    st.markdown("""<style>
        html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117; color: #FFFFFF; }
        .custom-metric { background-color: #1E1E1E; border: 1px solid #333; padding: 10px; border-radius: 8px; text-align: center; }
        .stInfo { background-color: #1A1D21 !important; color: #FFFFFF !important; }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
        html, body, [data-testid="stAppViewContainer"] { background-color: #FFFFFF; color: #000000; }
        .custom-metric { background-color: #F0F2F6; border: 1px solid #CCC; padding: 10px; border-radius: 8px; text-align: center; }
    </style>""", unsafe_allow_html=True)

st.title("🐕 Australian Dog Racing Trial")

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_losses = 0
    st.session_state.consecutive_wins = 0
    st.session_state.race_history = []
    st.session_state.last_bet_amount = 0.0

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.initial_bankroll = st.number_input("Starting Bankroll (\$)", value=1000.0)
    default_stake_pct = st.slider("Base Stake (%)", 0.1, 10.0, 1.0)
    st.session_state.use_perpetual = st.checkbox("🔁 Perpetual Race Run Mode", value=True)
    st.button("🌓 Toggle Theme", on_click=toggle_theme)
    if st.button("🔁 Reset Data"):
        st.session_state.clear()
        st.rerun()

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=pnl)
col3.metric("Streak", f"{st.session_state.consecutive_wins}W / {st.session_state.consecutive_losses}L")

# --- PERPETUAL MODE LOGIC ---
if st.session_state.use_perpetual:
    st.subheader("🔁 Race Entry")
    
    odds_bracket = st.selectbox("Select Odds Bracket", ["1.25–1.50", "1.51–2.00", "2.01+"])
    
    # Map bracket to a representative odds value for the calculation
    bracket_map = {"1.25–1.50": 1.35, "1.51–2.00": 1.75, "2.01+": 2.10}
    current_odds = bracket_map[odds_bracket]
    
    # --- NEW EDGE LOGIC FROM SPREADSHEET ---
    # 1. Implied
    implied_prob = (1 / current_odds) * 100
    
    # 2. Over Indexing (Based on Lost Streak)
    # If wins > 0, we treat streak as 1 for the base calculation, or 0 if paused
    streak_val = st.session_state.consecutive_losses if st.session_state.consecutive_losses > 0 else 1
    over_indexing = streak_val * 60.0 # The 60% multiplier from your sheet
    
    # 3. Weighted & Edge
    # Constant 7.04 derived from the sheet's relationship between 1.67 avg and odds
    weighted_prob = 7.04 + over_indexing
    edge_val = weighted_prob - implied_prob

    # UI for Edge
    edge_color = "green" if edge_val > 0 else "red"
    st.markdown(f"""
    <div style="background-color: #1E3A5F; color: white; padding: 15px; border-radius: 10px; border: 1px solid #333;">
        <b style="font-size: 1.1em;">📊 Model Edge Analysis</b>

        Current Odds: <b>{current_odds}</b> | Implied: <b>{implied_prob:.2f}%</b>

        Lost Streak Factor: <b>{streak_val}</b> | Over Indexing: <b>{over_indexing:.2f}%</b>

        Weighted Probability: <b>{weighted_prob:.2f}%</b>

        <span style="font-size: 1.2em;">Calculated Edge: <b style="color: {edge_color};">{edge_val:.2f}%</b></span>
    </div>
    """, unsafe_allow_html=True)

    # Stake Calculation
    if st.session_state.consecutive_losses == 0:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    else:
        mult = 5 if current_odds < 1.50 else (3 if current_odds <= 2.00 else 2)
        recommended_stake = st.session_state.last_bet_amount * mult

    st.info(f"💡 Recommended Stake: **\${recommended_stake:,.2f}**")

    # Result Buttons
    c1, c2 = st.columns(2)
    if c1.button("✅ WIN", use_container_width=True):
        st.session_state.bankroll += (recommended_stake * current_odds) - recommended_stake
        st.session_state.consecutive_wins += 1
        st.session_state.consecutive_losses = 0
        st.session_state.last_bet_amount = recommended_stake
        st.rerun()
    if c2.button("❌ LOSS", use_container_width=True):
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_losses += 1
        st.session_state.consecutive_wins = 0
        st.session_state.last_bet_amount = recommended_stake
        st.rerun()

# --- EDGE EXPLAINER ---
st.markdown("---")
with st.expander("ℹ️ How your Edge is calculated"):
    st.markdown(f"""
    This model uses a **Weighted Probability** approach based on your specific spreadsheet logic:
    
    1.  **Implied Probability**: Calculated directly from the market odds (\$1 / Odds\$).
    2.  **Over Indexing**: Your "Lost Streak Bet Number" multiplied by your base factor (**60%**).
    3.  **Weighted Probability**: We take a base constant (**7.04%**) and add your current **Over Indexing** value.
    4.  **The Edge**: The difference between the **Weighted Probability** and the **Implied Probability**.
    
    *Example from your sheet:*  
    Odds of **2.0** (50% Implied) at a **Lost Streak of 2** (120% Over Indexing) results in a **35% Edge**.
    """)
