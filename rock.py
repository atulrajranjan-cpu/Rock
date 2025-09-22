import streamlit as st
import random
import time

# --- Game Variables ---
choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3  # Best of 5

# --- Streamlit Session State ---
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'computer_score' not in st.session_state:
    st.session_state.computer_score = 0
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'winner_message' not in st.session_state:
    st.session_state.winner_message = ""
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# --- Game Logic ---
def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "It's a tie!"
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        st.session_state.player_score += 1
        return "You win this round! 🎉"
    else:
        st.session_state.computer_score += 1
        return "Computer wins this round! 💻"

# --- Main App Body ---
st.title("Rock, Paper, Scissors! 🪨📄✂️")
st.markdown("Play against the computer by clicking a button. First to 3 wins!")

st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

if not st.session_state.game_started:
    if st.button("Start Game"):
        st.session_state.game_started = True
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        st.rerun()
else:
    if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
        if st.session_state.player_score > st.session_state.computer_score:
            st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
        else:
            st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
        
        st.session_state.game_started = False
        st.session_state.game_active = False
        st.session_state.winner_message = ""
        
        if st.button("Play Again?"):
            st.rerun()

    else:
        st.write("Click your choice to play the next round!")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Rock 🪨"):
                player_choice = "rock"
                computer_choice = random.choice(choices)
                st.write(f"You chose: **{player_choice.upper()}**")
                st.write(f"Computer chose: **{computer_choice.upper()}**")
                result = determine_winner(player_choice, computer_choice)
                st.subheader(result)
        with col2:
            if st.button("Paper 📄"):
                player_choice = "paper"
                computer_choice = random.choice(choices)
                st.write(f"You chose: **{player_choice.upper()}**")
                st.write(f"Computer chose: **{computer_choice.upper()}**")
                result = determine_winner(player_choice, computer_choice)
                st.subheader(result)
        with col3:
            if st.button("Scissors ✂️"):
                player_choice = "scissors"
                computer_choice = random.choice(choices)
                st.write(f"You chose: **{player_choice.upper()}**")
                st.write(f"Computer chose: **{computer_choice.upper()}**")
                result = determine_winner(player_choice, computer_choice)
                st.subheader(result)

        st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")
