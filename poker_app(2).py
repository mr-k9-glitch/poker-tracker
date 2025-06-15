import streamlit as st
import pandas as pd
import altair as alt
import json

# Rotate dealer to next index
def rotate_dealer(dealer_index, num_players):
    return (dealer_index + 1) % num_players

# Load game state if exists
def load_game():
    try:
        with open("game_state.json") as f:
            state = json.load(f)
            for k, v in state.items():
                st.session_state[k] = v
    except FileNotFoundError:
        pass

# Save game state
def save_game():
    state = {k: v for k, v in st.session_state.items()}
    with open("game_state.json", "w") as f:
        json.dump(state, f)

# Main Streamlit App
def main():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1604479693470-3f03eec51bcd");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("♠️ Poker Game Profit/Loss Tracker")

    load_game()

    if "participants" not in st.session_state:
        st.session_state.participants = []
        st.session_state.total_balances = []
        st.session_state.dealer_index = 0
        st.session_state.round = 1
        st.session_state.history = []

    # Input participants only once
    if not st.session_state.participants:
        names_input = st.text_input("Enter participant names (comma-separated):")
        if st.button("Start Game") and names_input:
            st.session_state.participants = [name.strip() for name in names_input.split(",")]
            st.session_state.total_balances = [0.0] * len(st.session_state.participants)

    if st.session_state.participants:
        st.subheader(f"Round {st.session_state.round}")
        dealer = st.session_state.participants[st.session_state.dealer_index]
        st.info(f"🎲 Current Dealer: **{dealer}**")

        results = []
        st.write("Enter gains (+) or losses (-) for each player:")
        for name in st.session_state.participants:
            result = st.number_input(f"{name}:", key=f"round_{st.session_state.round}_{name}")
            results.append(result)

        if st.button("Submit Round"):
            if abs(sum(results)) > 0.01:
                st.warning("⚠️ Total net result is not zero. Please double-check the values.")
            st.session_state.total_balances = [
                total + result for total, result in zip(st.session_state.total_balances, results)
            ]
            st.session_state.history.append(list(st.session_state.total_balances))
            st.session_state.dealer_index = rotate_dealer(
                st.session_state.dealer_index, len(st.session_state.participants)
            )
            st.session_state.round += 1
            save_game()

        # Leaderboard
        st.subheader("📋 Leaderboard")
        df_leader = pd.DataFrame({
            "Player": st.session_state.participants,
            "Balance": st.session_state.total_balances
        }).sort_values(by="Balance", ascending=False)
        st.dataframe(df_leader)

        max_gain = max(st.session_state.total_balances)
        winner = st.session_state.participants[st.session_state.total_balances.index(max_gain)]
        st.success(f"🏆 Top Player So Far: **{winner}** with **{max_gain:.2f}** units")

        # Graph
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history, columns=st.session_state.participants)
            df["Round"] = range(1, len(df)+1)
            df = df.melt("Round", var_name="Player", value_name="Balance")
            chart = alt.Chart(df).mark_line(point=True).encode(
                x="Round",
                y="Balance",
                color="Player"
            ).properties(title="📊 Total Balance Over Rounds")
            st.altair_chart(chart, use_container_width=True)

        if st.button("End Game"):
            st.subheader("🏁 Final Summary")
            for name, balance in zip(st.session_state.participants, st.session_state.total_balances):
                status = "gained" if balance >= 0 else "lost"
                st.write(f"**{name}** {status} **{abs(balance):.2f}** units.")
            st.balloons()
            save_game()

            if st.button("Start New Game"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

if __name__ == "__main__":
    main()
