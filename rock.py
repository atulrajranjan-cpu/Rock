import streamlit as st
import cv2
import mediapipe as mp
import random
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3  # Best of 5


# --- Gesture Detection Function ---
def get_gesture(hand_landmarks):
    if not hand_landmarks:
        return None

    landmarks = hand_landmarks.landmark

    # Rock
    if (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y >
        landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y >
        landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y >
        landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.PINKY_TIP].y >
        landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return 'rock'

    # Paper
    elif (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
          landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
          landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y <
          landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.PINKY_TIP].y <
          landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return 'paper'

    # Scissors
    elif (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
          landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
          landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y >
          landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.PINKY_TIP].y >
          landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return 'scissors'

    return None


# --- Winner Determination ---
def get_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "tie"
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        return "player"
    else:
        return "computer"


# --- Streamlit App ---
def main():
    st.title("✊✋✌ Rock, Paper, Scissors with Hand Gestures")
    st.write("Show your gesture in front of the camera!")

    run = st.checkbox("Start Game")
    FRAME_WINDOW = st.image([])
    cap = cv2.VideoCapture(0)

    player_score = 0
    computer_score = 0

    while run and player_score < rounds_to_win and computer_score < rounds_to_win:
        ret, frame = cap.read()
        if not ret:
            st.write("Failed to access webcam")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        player_choice = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                player_choice = get_gesture(hand_landmarks)

        if player_choice:
            computer_choice = random.choice(choices)
            winner = get_winner(player_choice, computer_choice)

            if winner == "player":
                player_score += 1
                text = f"You: {player_choice} | Computer: {computer_choice} → You Win 🎉"
            elif winner == "computer":
                computer_score += 1
                text = f"You: {player_choice} | Computer: {computer_choice} → Computer Wins 🤖"
            else:
                text = f"You: {player_choice} | Computer: {computer_choice} → Tie 😅"

            cv2.putText(frame, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(frame, f"Score - You: {player_score} | Computer: {computer_score}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            time.sleep(2)  # pause between rounds

        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    cap.release()

    if player_score >= rounds_to_win:
        st.success(f"🎊 Congratulations! You won {player_score} - {computer_score}")
    elif computer_score >= rounds_to_win:
        st.error(f"😢 Computer won {computer_score} - {player_score}")


if __name__ == "__main__":
    main()

