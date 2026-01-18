import streamlit as st
import pandas as pd
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
    st.session_state.current_race_index = 0
    st.session_state.current_odds = 1.67
    st.session_state.mode = None  # 'race_day' or 'perpetual'

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if 'temp_bankroll' not in st.session_state:
        st.session_state.temp_bankroll = 1000.0
    new_bankroll = st.number_input(
        "Starting Bankroll (\$)",
        min_value=10.0,
        value=st.session_state.initial_bankroll,
        step=10.0
    )
    if new_bankroll != st.session_state.initial_bankroll:
        st.session_state.initial_bankroll = new_bankroll
        st.session_state.bankroll = new_bankroll
        st.session_state.last_bet_amount = 0.0

    base_stake_pct = st.slider(
        "Base Stake (% of Bankroll)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        format="%.1f%%"
    ) / 100.0

    win_rate_base = st.slider("Win Rate (Assumed)", 0.01, 1.00, 0.60, format="%.2f")

    if st.button("🌓 Toggle Theme"):
        toggle_theme()

    if st.button("🔁 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- TODAY'S RACES ---
race_day_races = [
    "Flemington • Race 4 - 14. Yes I Know (2)",
    "Flemington • Race 5 - 6. Celerity (4)",
    "Doomben • Race 3 - 14. Stein (6)",
    "Doomben • Race 5 - 9. Noble Decree (5)",
    "Rosehill • Race 8 - 5. Band Of Brothers (1)",
    "Ascot • Race 3 - 6. Our Paladin Al (1)",
    "Flemington • Race 10 - 8. Sass Appeal (9)",
    "Gold Coast • Race 8 - 1. Ninja (17)",
    "Rosehill • Race 10 - 7. Cross Tasman (3)",
    "Doomben • Race 8 - 7. Ten Deep (1)"
]

# --- MAIN INTERFACE ---
st.title("🐕 Datura Dog Racing Model")

# Top Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:,.2f}")
col3.metric("Win Streak", f"{st.session_state.consecutive_wins}W")

st.divider()

# --- MODE SELECTION ---
mode_col1, mode_col2 = st.columns(2)
if mode_col1.button("🎯 Start Race Day", use_container_width=True):
    st.session_state.mode = 'race_day'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.rerun()

if mode_col2.button("🔁 Start Perpetual Run", use_container_width=True):
    st.session_state.mode = 'perpetual'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.rerun()

# --- DISPLAY MODE ---
if st.session_state.mode == 'race_day':
    st.info("🏁 Race Day Mode: Automatic race progression")
elif st.session_state.mode == 'perpetual':
    st.info("🌀 Perpetual Mode: Continuous cycle, resets after 2 wins")
else:
    st.info("Select a mode to begin.")
    st.stop()

# --- CURRENT RACE ---
if st.session_state.mode == 'race_day':
    if st.session_state.current_race_index >= len(race_day_races):
        st.success("🎉 All races completed!")
        st.stop()
    race_str = race_day_races[st.session_state.current_race_index]
else:
    race_str = f"Perpetual Race #{st.session_state.current_race_index + 1}"

# Parse race
if st.session_state.mode == 'race_day':
    try:
        track_race_part = race_str.split("-")[0].strip()
        horse_part = "-".join(race_str.split("-")[1:]).strip()
        barrier = horse_part.split("(")[-1].strip(")")
        horse_name = horse_part.split(f"({barrier})")[0].strip()
        full_race_label = f"{track_race_part} - {horse_name} (Barrier {barrier})"
    except:
        full_race_label = race_str
        barrier = "Unknown"
else:
    full_race_label = race_str
    barrier = "N/A"

st.subheader("Current Race")
st.markdown(f"**{full_race_label}**")

# --- ODDS INPUT ---
st.subheader("Enter Bookmaker Odds")
odds_input = st.number_input(
    "Odds",
    min_value=1.01,
    value=st.session_state.current_odds,
    step=0.01,
    format="%.2f",
    key="odds_input"
)
st.session_state.current_odds = odds_input

# --- DISPLAY ODDS THRESHOLDS (ONLY IN PERPETUAL MODE) ---
if st.session_state.mode == 'perpetual':
    required_odds_40 = 1.40 / win_rate_base
    required_odds_45 = 1.45 / win_rate_base
    required_odds_50 = 1.50 / win_rate_base

    st.info(f"""
    🔍 **Odds Threshold Guide (Perpetual Run)**
    - For **+40% edge**: Need odds ≥ {required_odds_40:.2f}
    - For **+45% edge**: Need odds ≥ {required_odds_45:.2f}
    - For **+50%+ edge**: Need odds ≥ {required_odds_50:.2f}
    """, icon="📊")

# --- DATORA EDGE ---
datura_edge_decimal = (win_rate_base * st.session_state.current_odds) - 1
datura_edge_percent = datura_edge_decimal * 100

# Implied probability
implied_prob = (1 / st.session_state.current_odds) * 100

# --- RECOMMENDED STAKE ---
if st.session_state.consecutive_wins >= 2:
    recommended_stake = 0.0
    st.warning("⏸️ 2 Wins in a row. Paused betting until a loss occurs.")
else:
    if st.session_state.consecutive_wins > 0:
        recommended_stake = st.session_state.bankroll * base_stake_pct
    elif st.session_state.last_bet_amount == 0:
        recommended_stake = st.session_state.bankroll * base_stake_pct
    else:
        if st.session_state.current_odds > 2.00:
            recommended_stake = st.session_state.last_bet_amount * 2
        elif 1.50 < st.session_state.current_odds <= 2.00:
            recommended_stake = st.session_state.last_bet_amount * 3
        elif 1.25 < st.session_state.current_odds <= 1.50:
            recommended_stake = st.session_state.last_bet_amount * 5
        else:
            recommended_stake = st.session_state.bankroll * base_stake_pct

    recommended_stake = min(recommended_stake, st.session_state.bankroll)

# --- DISPLAY OUTPUT ---
st.markdown(f"**Implied Prob:** {implied_prob:.2f}%")
st.markdown(f"**Win Rate Assumed:** {win_rate_base:.2%}")
edge_color = "green" if datura_edge_decimal > 0 else "red"
st.markdown(f"### **Datura Edge:** :{edge_color}[{datura_edge_percent:+.2f}%]")

if recommended_stake > 0:
    st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")
else:
    st.info("No bet recommended (2-win pause).")

# --- WIN/LOSS BUTTONS ---
st.divider()
col_win, col_loss = st.columns(2)

def log_and_advance(result: str, profit: float):
    st.session_state.race_history.append({
        "race": full_race_label,
        "odds": st.session_state.current_odds,
        "stake": recommended_stake,
        "result": result,
        "profit": profit,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    st.session_state.current_race_index += 1
    st.session_state.current_odds = 1.67

if col_win.button("✅ WIN", use_container_width=True):
    if st.session_state.consecutive_wins < 2:
        profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * base_stake_pct
        log_and_advance("WIN", profit)
        st.rerun()
    else:
        st.warning("Already at 2 wins. No bet placed.")

if col_loss.button("❌ LOSS", use_container_width=True):
    st.session_state.bankroll -= recommended_stake
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = recommended_stake
    log_and_advance("LOSS", -recommended_stake)
    st.rerun()

# --- RACE HISTORY ---
if st.session_state.race_history:
    st.divider()
    st.subheader("📋 Race History")
    history_df = pd.DataFrame(st.session_state.race_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)

# --- EXPLAINER ---
with st.expander("ℹ️ Logic & Rules"):
    st.markdown("""
    ### **Datura Edge**
    - **Formula**: `(Win Rate × Odds) - 1`
    - Positive if > 0 → +EV bet

    ### **Odds Threshold Guide (Perpetual Mode)**
    - Shows minimum odds needed for key edge levels:
      - +40%, +45%, +50% based on your win rate
    - Helps identify value opportunities quickly

    ### **Stake Rules**
    - **Base Stake**: Adjustable % of current bankroll (default 1%)
    - **After WIN**: Reset to base % of *current* bankroll
    - **After LOSS**: Multiply last losing stake
      - > \$2.00 → 2×
      - \$1.50–\$2.00 → 3×
      - \$1.25–\$1.50 → 5×
    - **After 2 Wins**: Pause → next bet resets after loss

    P&L correctly tracks: `Current Bankroll - Initial Bankroll`
    """)
