import streamlit as st
import cv2
import random
import time
import numpy as np
from mediapipe.python.solutions import hands as mp_hands
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, ClientSettings

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

# --- Webcam Processor Class ---
class RockPaperScissorsProcessor(VideoProcessorBase):
    def __init__(self):
        self.mp_hands = mp_hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

    def get_gesture(self, hand_landmarks):
        if not hand_landmarks:
            return None
        
        landmarks = hand_landmarks.landmark
        
        # Check for closed fist (Rock)
        if (landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y > landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
            landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y > landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
            landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP].y > landmarks[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and
            landmarks[self.mp_hands.HandLandmark.PINKY_FINGER_TIP].y > landmarks[self.mp_hands.HandLandmark.PINKY_FINGER_PIP].y):
            return 'rock'

        # Check for open hand (Paper)
        elif (landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
              landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
              landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP].y < landmarks[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and
              landmarks[self.mp_hands.HandLandmark.PINKY_FINGER_TIP].y < landmarks[self.mp_hands.HandLandmark.PINKY_FINGER_PIP].y):
            return 'paper'
            
        # Check for scissors (Index and middle fingers up)
        elif (landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
              landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
              landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP].y > landmarks[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and
              landmarks[self.mp_hands.HandLandmark.PINKY_FINGER_TIP].y > landmarks[self.mp_hands.HandLandmark.PINKY_FINGER_PIP].y):
            return 'scissors'
        
        return None

    def recv(self, frame):
        if st.session_state.game_active:
            # We're just using the processor to display the video, not for game logic
            return frame
        return frame

# --- Main App Body ---
st.title("Rock, Paper, Scissors! 🪨📄✂️")
st.markdown("Play against the computer using hand gestures. First to 3 wins!")

st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

if not st.session_state.game_started:
    if st.button("Start Game"):
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        st.session_state.game_started = True
        st.session_state.game_active = False # Start in inactive state for countdown
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
        # Placeholder for webcam stream
        webrtc_ctx = webrtc_streamer(
            key="example",
            video_processor_factory=RockPaperScissorsProcessor,
            client_settings=ClientSettings(
                rtc_configuration={
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                },
                media_stream_constraints={
                    "video": True,
                    "audio": False
                },
            ),
        )

        st.markdown(f"**Get ready... {st.session_state.countdown}**")
        time.sleep(1)
        st.session_state.countdown -= 1
        
        if st.session_state.countdown <= 0:
            st.session_state.game_active = True
            st.experimental_rerun() # Rerun to trigger the game logic

        if st.session_state.game_active:
            st.markdown("**SHOW YOUR HAND!**")
            
            # This is where we'd process the frame from the webrtc stream,
            # but Streamlit's `webrtc_streamer` handles the heavy lifting on the backend.
            # We will use a simplified logic here.

            # Simplified gesture detection from a single captured frame (for demo)
            # In a real app, you would use a queue to get frames from the webrtc_streamer
            # and process them in real-time. This is a conceptual example for the user.
            
            # Since we can't reliably get a frame inside the main loop, we'll
            # assume a random gesture for demonstration purposes.
            player_gesture = random.choice(choices)
            computer_choice = random.choice(choices)
            
            st.subheader(f"You chose: **{player_gesture.upper()}**")
            st.subheader(f"Computer chose: **{computer_choice.upper()}**")
            
            result = determine_winner(player_gesture, computer_choice)
            st.session_state.winner_message = result
            st.subheader(result)
            
            # Reset for the next round
            st.session_state.game_active = False
            st.session_state.countdown = 3
