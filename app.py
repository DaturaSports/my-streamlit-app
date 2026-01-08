# --- PERPETUAL RUN MODE ---
if st.session_state.use_perpetual:
    st.markdown("---")
    st.subheader("🔁 Perpetual Race Run Mode")
    st.info("Select an odds bracket to get stake recommendation.")

    # Only three brackets
    odds_bracket = st.selectbox(
        "Select Odds Bracket",
        [
            "1.25–1.50",
            "1.51–2.00",
            "2.01+"
        ],
        key="perp_odds_select"
    )

    # Map bracket to internal odds for calculation
    bracket_to_odds = {
        "1.25–1.50": 1.50,
        "1.51–2.00": 1.75,
        "2.01+": 2.10
    }
    current_odds = bracket_to_odds[odds_bracket]

    # Extract upper bound of bracket for % increase calc
    if odds_bracket == "1.25–1.50":
        base_odds = 1.50
    elif odds_bracket == "1.51–2.00":
        base_odds = 2.00
    else:  # "2.01+"
        base_odds = 2.01  # Use floor of bracket

    # Calculate uplifts
    p40 = base_odds * 1.40
    p45 = base_odds * 1.45
    p50 = base_odds * 1.50

    # Display info box
    st.markdown(f"""
    <div style="
        background-color: #1E3A5F; 
        color: #FFFFFF; 
        padding: 12px; 
        border-radius: 6px; 
        font-family: 'Courier New', monospace; 
        font-size: 0.95em;
        border: 1px solid #333;
        margin: 10px 0;">
        <strong>📊 Odds Progression Guide</strong>

        Selected: <strong>{odds_bracket}</strong>

        +40% → up to <strong>\${p40:.2f}</strong>

        +45% → up to <strong>\${p45:.2f}</strong>

        +50% → up to <strong>\${p50:.2f}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 🏁 Race {st.session_state.race_index + 1} (Perpetual)")
    st.markdown(f"**Selected Odds Bracket:** `{odds_bracket}`")

    st.info(betting_status)

    # --- STAKE CALCULATION ---
    recommended_stake = 0.0

    if st.session_state.just_resumed:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    elif st.session_state.betting_active:
        if st.session_state.consecutive_losses == 0:
            recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
        else:
            base_stake = st.session_state.last_bet_amount
            if odds_bracket == "2.01+":
                multiplier = 2
            elif odds_bracket == "1.51–2.00":
                multiplier = 3
            elif odds_bracket == "1.25–1.50":
                multiplier = 5
            else:
                multiplier = 1
            recommended_stake = base_stake * multiplier
    else:
        recommended_stake = 0.0

    if recommended_stake > st.session_state.bankroll:
        recommended_stake = st.session_state.bankroll
        st.warning("📉 Stake reduced to available bankroll.")

    if st.session_state.just_resumed:
        st.info(f"💡 **Recommended Stake:** \${recommended_stake:,.2f} (Reset after pause)")
    elif st.session_state.betting_active:
        st.info(f"💡 **Recommended Stake:** \${recommended_stake:,.2f}")
    else:
        st.info(betting_status)

    # --- RESULT BUTTONS ---
    st.markdown("### Record Result")
    st.markdown('<div class="result-button-container">', unsafe_allow_html=True)
    col_win, col_loss = st.columns(2)
    with col_win:
        if st.button("✅ Win", key="btn_win_perp"):
            st.session_state.result_input = "Win"
            st.session_state.current_perp_bracket = odds_bracket
            st.session_state.current_perp_odds = current_odds
            st.rerun()
    with col_loss:
        if st.button("❌ Loss", key="btn_loss_perp"):
            st.session_state.result_input = "Loss"
            st.session_state.current_perp_bracket = odds_bracket
            st.session_state.current_perp_odds = current_odds
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
