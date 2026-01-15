import streamlit as st

# --- THEME & UI SETUP ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

st.set_page_config(page_title="Datura Edge Tracker", layout="wide")

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.streak = 1  # Matches 'Current Streak' in your sheet
    st.session_state.last_bet_amount = 0.0

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.session_state.initial_bankroll = st.number_input("Starting Bankroll (\$)", value=1000.0)
    win_rate_base = st.slider("Overall Win Rate (%)", 1.0, 100.0, 60.0) / 100
    base_stake_pct = st.slider("Base Stake (%)", 0.1, 10.0, 1.0)
    if st.button("🌓 Toggle Theme"):
        toggle_theme()
        st.rerun()
    if st.button("🔁 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🐕 Datura Dog Racing Model")

# Top Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
c1, c2, c3 = st.columns(3)
c1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
c2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:,.2f}")
c3.metric("Current Streak", st.session_state.streak)

st.divider()

# --- CALCULATION ENGINE ---
col_input, col_display = st.columns([1, 1])

with col_input:
    st.subheader("Race Parameters")
    # Manual Odds Input
    bookie_odds = st.number_input("Enter Bookmaker Odds", min_value=1.01, value=1.67, step=0.05)
    
    # 1. Implied Probability
    implied_prob = (1 / bookie_odds) * 100
    
    # 2. Over/Under Index (Matches Column D)
    # Formula: Current Streak * Overall Win Rate
    ou_index = (st.session_state.streak * (win_rate_base * 100))
    
    # 3. Datura Weighted Probability (Matches Column G)
    # Formula: (OU Index + Implied Prob) / 2
    weighted_prob = (ou_index + implied_prob) / 2
    
    # 4. Datura Edge (Matches Column H)
    # Formula: Weighted Prob - Implied Prob
    datura_edge = weighted_prob - implied_prob

with col_display:
    st.subheader("Model Analysis")
    
    # Using st.info and standard markdown to avoid HTML artifacts
    st.markdown(f"**Implied Probability:** {implied_prob:.2f}%")
    st.markdown(f"**Over/Under Index:** {ou_index:.2f}%")
    st.markdown(f"**Datura Weighted Prob:** {weighted_prob:.2f}%")
    
    edge_color = "green" if datura_edge > 0 else "red"
    st.markdown(f"### Datura Edge: :{edge_color}[{datura_edge:.2f}%]")
    
    # Staking Logic
    recommended_stake = st.session_state.bankroll * (base_stake_pct / 100)
    if st.session_state.streak > 1:
        # Recovery multiplier based on streak
        recommended_stake = recommended_stake * st.session_state.streak

    st.success(f"Recommended Stake: **\${recommended_stake:,.2f}**")

# --- ACTION BUTTONS ---
st.divider()
btn_win, btn_loss = st.columns(2)

if btn_win.button("✅ RACE WIN", use_container_width=True):
    profit = (recommended_stake * bookie_odds) - recommended_stake
    st.session_state.bankroll += profit
    # If we were in a losing streak, reset to -1 (Wins in a row). 
    # If already winning, increment the negative streak.
    if st.session_state.streak > 0:
        st.session_state.streak = -1
    else:
        st.session_state.streak -= 1
    st.rerun()

if btn_loss.button("❌ RACE LOSS", use_container_width=True):
    st.session_state.bankroll -= recommended_stake
    # If we were in a winning streak, reset to 1 (Losses in a row).
    # If already losing, increment the positive streak.
    if st.session_state.streak < 0:
        st.session_state.streak = 1
    else:
        st.session_state.streak += 1
    st.rerun()

# --- EXPLAINER ---
with st.expander("📖 Logic Explainer (Based on Spreadsheet)"):
    st.write("""
    **How the Edge is calculated:**
    1. **Implied Prob**: 1 / Bookie Odds.
    2. **Over/Under Index**: Your Current Streak multiplied by the 60% baseline.
    3. **Weighted Prob**: The average of the Implied Prob and the Over/Under Index.
    4. **Edge**: The difference between our Weighted Prob and the Bookie's Implied Prob.
    
    *Note: Positive streaks represent Losses in a Row. Negative streaks represent Wins in a Row.*
    """)
