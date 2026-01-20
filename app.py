import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- SESSION STATE INIT ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.race_history = []
    st.session_state.current_race_index = 0
    st.session_state.current_odds = 1.80
    st.session_state.mode = None
    st.session_state.auto_running = False
    st.session_state.speed = 1.0  # 1.0 = normal, 2.0 = fast, 0.5 = slow

# --- THEME TOGGLE ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

st.set_page_config(page_title="Datura Companion", layout="wide")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
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

    win_rate_base = st.slider("Expected Win Rate (Favourite)", 0.01, 1.00, 0.60, format="%.2f")

    # Auto Run Speed
    st.session_state.speed = st.select_slider(
        "Auto Run Speed",
        options=[0.5, 1.0, 2.0, 5.0],
        format_func=lambda x: "Slow" if x == 0.5 else "Normal" if x == 1.0 else "Fast" if x == 2.0 else "Max",
        value=1.0
    )

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
st.title("🐕 Datura Companion v1.2")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:+,.2f}")
col3.metric("Win Streak", f"{st.session_state.consecutive_wins}W")

st.divider()

# --- MODE SELECTION ---
mode_col1, mode_col2, mode_col3 = st.columns(3)
if mode_col1.button("🎯 Start Race Day", use_container_width=True):
    st.session_state.mode = 'race_day'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.auto_running = False
    st.rerun()

if mode_col2.button("🔁 Start Perpetual Run", use_container_width=True):
    st.session_state.mode = 'perpetual'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.auto_running = False
    st.rerun()

if mode_col3.button("▶️ Auto Run Simulation", use_container_width=True):
    if not st.session_state.mode:
        st.warning("Please select a mode first.")
    else:
        st.session_state.auto_running = True
        st.rerun()

# --- DISPLAY MODE STATUS ---
if st.session_state.mode == 'race_day':
    st.info("🏁 Race Day Mode: Pause after 2 wins until a loss occurs")
elif st.session_state.mode == 'perpetual':
    st.info("🌀 Perpetual Mode: Reset stake after win. No pause.")
else:
    st.info("Select a mode to begin.")
    st.stop()

# --- AUTO RUN CONTROL BAR ---
if st.session_state.auto_running:
    st.warning("▶️ Auto Run Active — Simulating...")
    col_a, col_b = st.columns([1, 1])
    if col_a.button("⏸️ Pause Auto Run"):
        st.session_state.auto_running = False
        st.rerun()
    if col_b.button("⏹️ Stop & Reset"):
        st.session_state.auto_running = False
        st.session_state.mode = None
        st.rerun()
    st.divider()

# --- CURRENT RACE ---
if st.session_state.mode == 'race_day':
    if st.session_state.current_race_index >= len(race_day_races):
        st.success("🎉 All races completed!")
        st.session_state.auto_running = False
        st.stop()
    race_str = race_day_races[st.session_state.current_race_index]
else:
    race_str = f"Perpetual Race #{st.session_state.current_race_index + 1}"

try:
    if st.session_state.mode == 'race_day':
        track_race_part = race_str.split("-")[0].strip()
        horse_part = "-".join(race_str.split("-")[1:]).strip()
        barrier = horse_part.split("(")[-1].strip(")")
        horse_name = horse_part.split(f"({barrier})")[0].strip()
        full_race_label = f"{track_race_part} - {horse_name} (Barrier {barrier})"
    else:
        full_race_label = race_str
        barrier = "N/A"
except Exception:
    full_race_label = race_str
    barrier = "Unknown"

st.subheader("Current Race")
st.markdown(f"**{full_race_label}**")

# --- ODDS INPUT ---
st.subheader("Enter Favourite Odds")
odds_input = st.number_input(
    "Favourite Odds",
    min_value=1.01,
    value=st.session_state.current_odds,
    step=0.01,
    format="%.2f",
    key="odds_input_live"
)
st.session_state.current_odds = odds_input

# --- ODDS DIFFERENTIAL GUIDE (Only in Perpetual Run) ---
if st.session_state.mode == 'perpetual':
    uplift_40 = st.session_state.current_odds * 1.40
    uplift_45 = st.session_state.current_odds * 1.45
    uplift_50 = st.session_state.current_odds * 1.50

    st.info(f"""
    🔍 **Odds Differential Guide (vs Favourite: {st.session_state.current_odds:.2f})**
    - **+40% longer odds**: {uplift_40:.2f}
    - **+45% longer odds**: {uplift_45:.2f}
    - **+50% longer odds**: {uplift_50:.2f}

    🎯 If the actual second favourite is **above these thresholds**, the market sees a **clear favorite** → stronger signal for **favourite play**.
    """, icon="📊")

# --- DATORA EDGE ---
implied_prob = 1 / st.session_state.current_odds
datura_edge_decimal = (win_rate_base * st.session_state.current_odds) - 1
datura_edge_percent = datura_edge_decimal * 100
implied_prob_percent = implied_prob * 100

# --- STAKE LOGIC (NO 5% CAP) ---
betting_allowed = True
if st.session_state.mode == 'race_day' and st.session_state.consecutive_wins >= 2:
    betting_allowed = False
    st.warning("⏸️ 2 wins in a row. Betting paused until a loss occurs.")

if not betting_allowed:
    recommended_stake = 0.0
    st.info("No bet recommended (awaiting loss after 2 wins).")
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

    # ✅ Removed 5% cap — stake can grow based on loss streak
    # Clamp only to available bankroll
    if recommended_stake > st.session_state.bankroll:
        st.warning(f"⚠️ Stake exceeds bankroll. Reduced to \${st.session_state.bankroll:,.2f}")
        recommended_stake = st.session_state.bankroll

    st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")

# --- DISPLAY EDGE ---
st.markdown(f"**Implied Prob:** {implied_prob_percent:.2f}%")
st.markdown(f"**Expected Win Rate:** {win_rate_base:.2%}")
edge_color = "green" if datura_edge_decimal > 0 else "red"
st.markdown(f"### **Datura Edge:** :{edge_color}[{datura_edge_percent:+.2f}%]")

# --- WIN/LOSS BUTTONS ---
st.divider()
col_win, col_loss = st.columns(2)

def log_and_advance(result: str, profit: float):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.race_history.append({
        "Race": full_race_label,
        "Odds": st.session_state.current_odds,
        "Stake": round(recommended_stake, 2),
        "Result": result,
        "Profit": round(profit, 2),
        "Bankroll": round(st.session_state.bankroll, 2),
        "Timestamp": timestamp
    })

    st.session_state.current_race_index += 1
    st.session_state.current_odds = 1.80

if col_win.button("✅ WIN", use_container_width=True):
    if not betting_allowed:
        st.warning("Cannot place bet — 2 wins already recorded.")
    else:
        profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * base_stake_pct
        log_and_advance("WIN", profit)
        st.rerun()

if col_loss.button("❌ LOSS", use_container_width=True):
    st.session_state.bankroll -= recommended_stake
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = recommended_stake
    log_and_advance("LOSS", -recommended_stake)
    st.rerun()

# --- AUTO RUN LOOP ---
if st.session_state.auto_running:
    time.sleep(2.0 / st.session_state.speed)  # Adjustable delay
    win_prob = 0.60  # Use win_rate_base or adjust per model
    if random.random() < win_prob:
        if col_win.button("Auto: WIN", key=f"auto_win_{int(time.time())}"):
            profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
            st.session_state.bankroll += profit
            st.session_state.consecutive_wins += 1
            st.session_state.last_bet_amount = st.session_state.bankroll * base_stake_pct
            log_and_advance("WIN", profit)
            st.rerun()
    else:
        if col_loss.button("Auto: LOSS", key=f"auto_loss_{int(time.time())}"):
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

    # --- PROFIT CHART ---
    st.subheader("📈 Profit Chart")
    chart_data = history_df[["Timestamp", "Bankroll"]].set_index("Timestamp")
    st.line_chart(chart_data["Bankroll"])

# --- EXPLAINER ---
with st.expander("ℹ️ Logic & Rules"):
    st.markdown("""
    ### **Datura Companion v1.2**
    - **Only bet on favourites** — no underdogs, no overlays
    - **Expected Win Rates**:
      - **NRL/AFL Favourites**: 65%
      - **Horses/Dogs (Start-of-Day Favourite)**: 60%
    - **Edge = (Expected Win Rate × Odds) - 1**
    - **Odds Differential**: Large gap → market confidence → stronger signal
    - **Staking**: Dynamic, based on loss streak and odds — **no 5% cap**
    - **Auto Run**: Simulate with configurable speed
    - **Profit Chart**: Track bankroll over time

    **No form analysis. No insider knowledge. Just market structure.**
    """)
