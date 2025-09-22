import streamlit as st
import cv2
import random
import time
import numpy as np

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
if 'countdown' not in st.session_state:
    st.session_state.countdown = 3
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# --- Hand Gesture Detection Logic (Simplified) ---
def get_gesture_from_image(image):
    # Convert the image to grayscale and apply a blur
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use a simple threshold to create a binary image
    _, thresh = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, image

    # Find the largest contour (assumed to be the hand)
    max_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(max_contour)

    # Check the area of the hand to determine the gesture
    if area > 10000: # Adjust this value based on camera distance
        # Get the convex hull and count defects to distinguish gestures
        hull = cv2.convexHull(max_contour)
        
        # Check for rock (fist): small contour area
        if area < 50000: # A smaller contour area can be a closed fist
            return 'rock', image

        # Check for paper (open hand): very large contour area
        elif area > 100000:
            return 'paper', image
        
        # We cannot reliably detect scissors with this simple method, so we'll
        # keep it simple and focus on rock and paper.
        return None, image
        
    return None, image

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
st.markdown("Play against the computer using hand gestures. First to 3 wins!")

st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

if not st.session_state.game_started:
    if st.button("Start Game"):
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        st.session_state.game_started = True
        st.session_state.game_active = False
        st.experimental_rerun()
else:
    if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
        if st.session_state.player_score > st.session_state.computer_score:
            st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
        else:
            st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
        
        st.session_state.game_started = False
        st.session_state.game_active = False
        st.session_state.winner_message = ""
        st.session_state.countdown = 3
        
        if st.button("Play Again?"):
            st.rerun()

    else:
        st.write("Show your hand gesture to the camera after the countdown.")
        countdown_placeholder = st.empty()
        
        for i in range(3, 0, -1):
            countdown_placeholder.markdown(f"**Get ready... {i}**", unsafe_allow_html=True)
            time.sleep(1)
        
        countdown_placeholder.markdown("**SHOW YOUR HAND!**", unsafe_allow_html=True)
        
        frame = st.camera_input("Take a photo of your hand")
        
        if frame is not None:
            file_bytes = np.asarray(bytearray(frame.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            player_gesture, img_with_contours = get_gesture_from_image(img)
            
            st.subheader("Your Move")
            st.image(img_with_contours, channels="BGR", caption="Your Hand")

            computer_choice = random.choice(choices)
            st.subheader("Computer's Move")
            st.write(f"Computer chose: **{computer_choice.upper()}**")

            if player_gesture:
                st.write(f"You chose: **{player_gesture.upper()}**")
                result = determine_winner(player_gesture, computer_choice)
                st.subheader(result)
            else:
                st.warning("Could not detect a clear gesture. Please try again.")
    
    # Final winner announcement
    if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
        if st.session_state.player_score > st.session_state.computer_score:
            st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
        else:
            st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
        
        st.session_state.game_started = False
        if st.button("Play Again?"):
            st.rerun()
            
if __name__ == '__main__':
    main()
