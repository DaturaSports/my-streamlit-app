import streamlit as st
import pandas as pd
import numpy as np
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Datura Intelligence", page_icon="🧠", layout="centered")
st.title("🧠 Datura Intelligence")
st.markdown("Live Edge Tracker v1.3 — Favourite Market Engine")

# --- SESSION STATE INITIALIZATION ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
if 'initial_bankroll' not in st.session_state:
    st.session_state.initial_bankroll = 1000.0
if 'mode' not in st.session_state:
    st.session_state.mode = 'race_day'  # 'race_day' or 'perpetual'
if 'base_stake_pct' not in st.session_state:
    st.session_state.base_stake_pct = 0.01
if 'last_bet_amount' not in st.session_state:
    st.session_state.last_bet_amount = 0.0
if 'consecutive_wins' not in st.session_state:
    st.session_state.consecutive_wins = 0
if 'bets_since_reset' not in st.session_state:
    st.session_state.bets_since_reset = 0
if 'max_consecutive_bets' not in st.session_state:
    st.session_state.max_consecutive_bets = 5
if 'race_history' not in st.session_state:
    st.session_state.race_history = []
if 'current_odds' not in st.session_state:
    st.session_state.current_odds = 1.80
if 'bet_result' not in st.session_state:
    st.session_state.bet_result = None

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("🎛️ Controls")
    st.session_state.mode = st.radio("Mode", ["race_day", "perpetual"], index=0)
    st.session_state.base_stake_pct = st.slider("Base Stake %", 0.5, 5, 1, 1) / 100.0
    st.session_state.max_consecutive_bets = st.number_input("Max Consecutive Bets", 1, 10, 5)

    if st.button("🔁 Reset All"):
        st.session_state.bankroll = st.session_state.initial_bankroll
        st.session_state.last_bet_amount = 0.0
        st.session_state.consecutive_wins = 0
        st.session_state.bets_since_reset = 0
        st.session_state.race_history = []
        st.session_state.bet_result = None
        st.success("✅ Reset complete")

    st.markdown("---")
    st.markdown("### 📊 Current State")
    st.write(f"Bankroll: \${st.session_state.bankroll:,.2f}")
    st.write(f"Mode: {st.session_state.mode}")
    st.write(f"Streak: {st.session_state.consecutive_wins} win(s)")
    st.write(f"Bets Since Reset: {st.session_state.bets_since_reset}")

# --- MAIN: INPUT SECTION ---
st.markdown("### 🎯 Current Bet")
col1, col2 = st.columns(2)
with col1:
    st.session_state.current_odds = st.number_input("Favourite Odds (Decimal)", 1.01, 10.0, 1.80, 0.01)
with col2:
    st.session_state.bet_result = st.radio("Result", ["WIN", "LOSS"], index=1 if st.session_state.bet_result == "LOSS" else 0)

# --- BETTING ALLOWED LOGIC ---
betting_allowed = True
disallow_reason = ""

# Drawdown check (20% from initial)
drawdown = (st.session_state.initial_bankroll - st.session_state.bankroll) / st.session_state.initial_bankroll
if drawdown > 0.20:
    betting_allowed = False
    disallow_reason = "🛑 20% drawdown reached — manual reset required"

# Race Day: Pause after 2 wins
if st.session_state.mode == 'race_day' and st.session_state.consecutive_wins >= 2:
    betting_allowed = False
    disallow_reason = "⏸️ 2 wins in a row. Betting paused until loss."

# Perpetual: Cap consecutive bets
if st.session_state.mode == 'perpetual' and st.session_state.bets_since_reset >= st.session_state.max_consecutive_bets:
    betting_allowed = False
    disallow_reason = f"⏸️ Max {st.session_state.max_consecutive_bets} bets reached. Resetting."

# Compute recommended stake
base_stake = st.session_state.bankroll * st.session_state.base_stake_pct

if not betting_allowed:
    recommended_stake = 0.0
    st.warning(disallow_reason)
else:
    if st.session_state.consecutive_wins > 0:
        # After win: reset to 1% of current bankroll
        recommended_stake = base_stake
    elif st.session_state.last_bet_amount == 0:
        # First bet
        recommended_stake = base_stake
    else:
        # After loss: multiply last stake based on odds
        if st.session_state.current_odds > 2.00:
            recommended_stake = st.session_state.last_bet_amount * 2
        elif 1.50 < st.session_state.current_odds <= 2.00:
            recommended_stake = st.session_state.last_bet_amount * 3
        elif 1.25 < st.session_state.current_odds <= 1.50:
            recommended_stake = st.session_state.last_bet_amount * 5
        else:
            recommended_stake = base_stake  # Fallback

    # Cap stake at 10% of initial bankroll (not current)
    max_stake_from_initial = st.session_state.initial_bankroll * 0.10
    recommended_stake = min(recommended_stake, max_stake_from_initial)

    st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")

# --- PROCESS RESULT ---
if st.button("✅ Confirm Bet Result"):
    if drawdown > 0.20:
        st.error("⚠️ 20% drawdown limit reached. Reset required.")
    else:
        stake = recommended_stake
        profit = 0.0

        if stake > st.session_state.bankroll:
            st.error(f"⚠️ Insufficient funds. Need \${stake:,.2f}, have \${st.session_state.bankroll:,.2f}")
        else:
            if st.session_state.bet_result == "WIN":
                profit = (st.session_state.current_odds * stake) - stake
                st.session_state.bankroll += profit
                st.session_state.consecutive_wins += 1
                st.session_state.last_bet_amount = st.session_state.bankroll * st.session_state.base_stake_pct  # Reset
                st.balloons()
            else:  # LOSS
                profit = -stake
                st.session_state.bankroll += profit
                st.session_state.consecutive_wins = 0
                st.session_state.last_bet_amount = stake  # Carry forward lost stake

            st.session_state.bets_since_reset += 1

            # Log to history
            st.session_state.race_history.append({
                'timestamp': pd.Timestamp.now(),
                'odds': st.session_state.current_odds,
                'stake': stake,
                'result': st.session_state.bet_result,
                'profit': profit,
                'bankroll_after': st.session_state.bankroll
            })

            st.success(f"✅ {st.session_state.bet_result} recorded. Bankroll: \${st.session_state.bankroll:,.2f}")

# --- RACE HISTORY ---
if st.session_state.race_history:
    st.markdown("### 📜 Recent Bets")
    hist_df = pd.DataFrame(st.session_state.race_history)
    hist_df = hist_df[['timestamp', 'odds', 'stake', 'result', 'profit', 'bankroll_after']]
    st.dataframe(hist_df.tail(10).round(2), use_container_width=True)

# --- DIAGNOSTIC LAYER ---
def run_diagnostics():
    history = st.session_state.race_history
    if len(history) < 50:
        st.info("📊 Diagnostics: Collecting data (need 50+ bets)")
        return

    wins = sum(1 for r in history if r['result'] == 'WIN')
    win_rate = wins / len(history)
    expected_wr = 0.60
    avg_odds = sum(r['odds'] for r in history) / len(history)
    expected_edge = (expected_wr * avg_odds) - 1
    realized_roi = sum(r['profit'] for r in history) / sum(r['stake'] for r in history if r['stake'] > 0)
    running_balance = [st.session_state.initial_bankroll]
    for r in history:
        running_balance.append(running_balance[-1] + r['profit'])
    peak = max(running_balance)
    current = running_balance[-1]
    max_drawdown = (peak - current) / peak if peak > 0 else 0

    loss_streaks = []
    current_loss_streak = 0
    for r in history:
        if r['result'] == 'LOSS':
            current_loss_streak += 1
        else:
            if current_loss_streak > 0:
                loss_streaks.append(current_loss_streak)
                current_loss_streak = 0
    max_loss_streak = max(loss_streaks) if loss_streaks else 0

    flags = []
    if win_rate < 0.58:
        flags.append(f"🔴 Win Rate {win_rate:.1%} < 58%")
    if realized_roi < expected_edge * 0.7:
        flags.append(f"🟡 Realized ROI {realized_roi:+.1%} < 70% of expected")
    if max_drawdown > 0.30:
        flags.append(f"🔴 Max Drawdown {max_drawdown:.1%} > 30%")
    if max_loss_streak >= 6:
        flags.append(f"⚠️ 6+ consecutive losses detected")

    with st.expander("🔍 Diagnostic Report", expanded=len(flags) > 0):
        st.markdown(f"**Total Bets:** {len(history)}")
        st.markdown(f"**Actual Win Rate:** :{'green' if win_rate >= 0.58 else 'red'}[{win_rate:.1%}]")
        st.markdown(f"**Avg Odds:** {avg_odds:.2f}")
        st.markdown(f"**Expected Edge:** {expected_edge:+.1%}")
        st.markdown(f"**Realized ROI:** {realized_roi:+.1%}")
        st.markdown(f"**Max Drawdown:** {max_drawdown:.1%}")
        st.markdown(f"**Worst Loss Streak:** {max_loss_streak}")

        if flags:
            for flag in flags:
                st.warning(flag)
        else:
            st.success("✅ No structural issues detected")

# Run diagnostics
run_diagnostics()

# --- FOOTER ---
st.markdown("---")
st.markdown("🧠 Datura Intelligence v1.3 — Formula-Adherent Sports Modeling Unit | Rei Labs")
