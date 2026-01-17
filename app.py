import streamlit as st
from datetime import datetime

# --- THEME & SESSION STATE INIT ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

st.set_page_config(page_title="Datura Dog Racing Model", layout="wide")

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.race_history = []
    st.session_state.selected_race = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.initial_bankroll = st.number_input("Starting Bankroll (\$)", value=1000.0)
    win_rate_base = st.slider("Overall Win Rate (%)", 1.0, 100.0, 60.0) / 100
    if st.button("🌓 Toggle Theme"):
        toggle_theme()
    if st.button("🔁 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- TODAY'S RACES ---
races = [
    "Flemington • Race 4 - 14. Yes I Know (2.00)",
    "Flemington • Race 5 - 6. Celerity (4.00)",
    "Doomben • Race 3 - 14. Stein (6.00)",
    "Doomben • Race 5 - 9. Noble Decree (5.00)",
    "Rosehill • Race 8 - 5. Band Of Brothers (1.00)",
    "Ascot • Race 3 - 6. Our Paladin Al (1.00)",
    "Flemington • Race 10 - 8. Sass Appeal (9.00)",
    "Gold Coast • Race 8 - 1. Ninja (17.00)",
    "Rosehill • Race 10 - 7. Cross Tasman (3.00)",
    "Doomben • Race 8 - 7. Ten Deep (1.00)"
]

# --- MAIN INTERFACE ---
st.title("🐕 Datura Dog Racing Model")

# Top Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:,.2f}")
col3.metric("Win Streak", f"{st.session_state.consecutive_wins}W")

# Divider
st.divider()

# --- RACE SELECTION ---
st.subheader("🎯 Select Race")
st.session_state.selected_race = st.selectbox("Choose a race:", races, index=None, placeholder="Select a race...")

if not st.session_state.selected_race:
    st.info("Please select a race to continue.")
else:
    # Parse race data
    parts = st.session_state.selected_race.split("(")
    name_part = parts[0].strip()
    odds = float(parts[1].strip(")"))
    
    # Extract horse number and name
    name_part_clean = name_part.split("-")[-1].strip()
    horse_info = f"{name_part.split('•')[0].strip()} • {name_part.split('•')[1].split('-')[0].strip()} - {name_part_clean}"

    st.markdown(f"**Selected:** {horse_info} | **Odds:** {odds}")

    # --- CALCULATIONS ---
    implied_prob = (1 / odds) * 100
    current_streak_for_index = st.session_state.consecutive_wins + 1  # Base index logic
    ou_index = current_streak_for_index * (win_rate_base * 100)
    weighted_prob = (ou_index + implied_prob) / 2
    datura_edge = weighted_prob - implied_prob

    # --- STAKE LOGIC (Your Exact Rules) ---
    if st.session_state.consecutive_wins >= 2:
        recommended_stake = 0.0
        st.warning("⏸️ 2 Wins in a row. Paused betting until a loss occurs.")
    else:
        if st.session_state.last_bet_amount == 0:
            # First bet or restarting after pause
            recommended_stake = st.session_state.bankroll * 0.01  # 1% base
        else:
            if odds > 2.00:
                recommended_stake = st.session_state.last_bet_amount * 2
            elif 1.50 < odds <= 2.00:
                recommended_stake = st.session_state.last_bet_amount * 3
            elif 1.25 < odds <= 1.50:
                recommended_stake = st.session_state.last_bet_amount * 5
            else:
                # Odds ≤ 1.25 — very low edge, use base 1%
                recommended_stake = st.session_state.bankroll * 0.01

    # Cap stake to available bankroll
    recommended_stake = min(recommended_stake, st.session_state.bankroll)

    # --- DISPLAY OUTPUT ---
    st.markdown(f"**Implied Prob:** {implied_prob:.2f}%")
    st.markdown(f"**Over/Under Index:** {ou_index:.2f}%")
    st.markdown(f"**Weighted Prob:** {weighted_prob:.2f}%")
    
    edge_color = "green" if datura_edge > 0 else "red"
    st.markdown(f"### **Datura Edge:** :{edge_color}[{datura_edge:.2f}%]")

    if recommended_stake > 0:
        st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")
    else:
        st.info("No bet recommended (2-win pause).")

    # --- ACTION BUTTONS ---
    st.divider()
    col_win, col_loss = st.columns(2)

    if col_win.button("✅ WIN", use_container_width=True):
        if st.session_state.selected_race:
            profit = (recommended_stake * odds) - recommended_stake
            st.session_state.bankroll += profit
            st.session_state.consecutive_wins += 1
            st.session_state.last_bet_amount = recommended_stake
            # Log race
            st.session_state.race_history.append({
                "race": horse_info,
                "odds": odds,
                "stake": recommended_stake,
                "result": "WIN",
                "profit": profit,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.session_state.selected_race = None
            st.rerun()

    if col_loss.button("❌ LOSS", use_container_width=True):
        if st.session_state.selected_race:
            st.session_state.bankroll -= recommended_stake
            st.session_state.consecutive_wins = 0  # Reset win streak
            st.session_state.last_bet_amount = recommended_stake
            # Log race
            st.session_state.race_history.append({
                "race": horse_info,
                "odds": odds,
                "stake": recommended_stake,
                "result": "LOSS",
                "profit": -recommended_stake,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.session_state.selected_race = None
            st.rerun()

# --- RACE HISTORY ---
if st.session_state.race_history:
    st.divider()
    st.subheader("📋 Race History")
    history_df = pd.DataFrame(st.session_state.race_history)
    st.dataframe(history_df, use_container_width=True)

# --- EXPLAINER ---
with st.expander("ℹ️ Stake & Edge Logic"):
    st.markdown("""
    ### **Edge Calculation**
    - **Implied Prob**: \$1 / \\text{Odds}\$
    - **Over/Under Index**: \$(\\text{Win Streak} + 1) \\times \\text{Win Rate}\$
    - **Weighted Prob**: \$(\\text{Index} + \\text{Implied}) / 2\$
    - **Edge**: \$\\text{Weighted} - \\text{Implied}\$

    ### **Stake Rules**
    - After a **loss**:
      - Odds > \$2.00 → **Double** last bet
      - \$1.50–\$2.00 → **Triple**
      - \$1.25–\$1.50 → **5×**
    - After **2 consecutive wins** → **Pause betting** until a loss.
    - First bet uses **1% of bankroll**.

    All logic is applied exactly as per your model.
    """)
