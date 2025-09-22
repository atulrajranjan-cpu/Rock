import streamlit as st
import cv2
import mediapipe as mp
import random
import time
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, ClientSettings

# --- Game Variables ---
choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3  # Best of 5

# --- Streamlit Session State ---
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'computer_score' not in st.session_state:
    st.session_state.computer_score = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# --- Webcam Processor Class ---
class RockPaperScissorsProcessor(VideoProcessorBase):
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.computer_choice = random.choice(choices)
        self.player_choice = None
        self.start_time = time.time()
        self.countdown = 3
        self.result = ""

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
        img = frame.to_ndarray(format="bgr24")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                self.player_choice = self.get_gesture(hand_landmarks)

        if st.session_state.game_active:
            if time.time() - self.start_time > 1:
                self.countdown -= 1
                self.start_time = time.time()

            if self.countdown <= 0:
                self.countdown = 3
                st.session_state.game_active = False

                if self.player_choice:
                    self.result = self.determine_winner(self.player_choice, self.computer_choice)
                else:
                    self.result = "Could not detect a clear gesture."

                st.session_state.player_choice = self.player_choice
                st.session_state.computer_choice = self.computer_choice
                st.session_state.result = self.result
                st.session_state.game_active = False
                st.rerun()
        
        if st.session_state.game_active:
            text = f"SHOW! ({self.countdown})"
        else:
            text = "Click 'Start Round' to begin!"
        
        cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        return img

    def determine_winner(self, player_choice, computer_choice):
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

# --- Main App UI ---
st.title("Rock, Paper, Scissors! 🪨📄✂️")

st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

webrtc_streamer(key="example", video_processor_factory=RockPaperScissorsProcessor,
    client_settings=ClientSettings(
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False}
    )
)

if st.session_state.get('result'):
    st.subheader(st.session_state.result)
    st.markdown(f"**Your Choice:** {st.session_state.player_choice.upper()}")
    st.markdown(f"**Computer Choice:** {st.session_state.computer_choice.upper()}")
    del st.session_state['result']

if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
    st.session_state.game_started = False
    st.session_state.game_active = False
    
    if st.session_state.player_score > st.session_state.computer_score:
        st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
    else:
        st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
    
    if st.button("Play Again?"):
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        st.rerun()

if st.button("Start Round"):
    st.session_state.game_active = True
    st.rerun()
