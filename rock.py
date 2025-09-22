import cv2
import mediapipe as mp
import random
import streamlit as st

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Game variables
player_score = 0
computer_score = 0
game_rounds = 5

# Streamlit App
st.title("Rock-Paper-Scissors: Hand Gesture Game")
st.write("Hold your hand in front of the camera to play!")
st.write("🖐️ Rock: 0 fingers up")
st.write("✌️ Scissors: 2 fingers up")
st.write("✋ Paper: 5 fingers up")

frame_placeholder = st.empty()
result_placeholder = st.empty()

# Function to count fingers
def count_fingers(landmarks):
    finger_tips = [8, 12, 16, 20]  # Indices for the tips of the index, middle, ring, and pinky fingers
    finger_up = []

    # Thumb check
    if landmarks[4].x < landmarks[2].x:
        finger_up.append(True)
    else:
        finger_up.append(False)

    # Other fingers check
    for tip_id in finger_tips:
        if landmarks[tip_id].y < landmarks[tip_id - 2].y:
            finger_up.append(True)
        else:
            finger_up.append(False)

    return finger_up.count(True)

# Main game loop
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    st.error("Error: Could not open webcam.")
else:
    while cap.isOpened() and player_score < game_rounds and computer_score < game_rounds:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a natural mirror-like view
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Hands
        result = hands.process(rgb_frame)

        player_choice = "Waiting..."
        computer_choice = "Waiting..."

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Get landmarks of the hand
                landmarks = hand_landmarks.landmark

                # Count the number of fingers up
                finger_count = count_fingers(landmarks)

                if finger_count == 0:
                    player_choice = "Rock"
                elif finger_count == 2:
                    player_choice = "Scissors"
                elif finger_count == 5:
                    player_choice = "Paper"
                else:
                    player_choice = "Waiting..."

                # Draw landmarks on the frame
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Computer's turn
        if player_choice != "Waiting...":
            choices = ["Rock", "Paper", "Scissors"]
            computer_choice = random.choice(choices)

            # Determine the winner
            with result_placeholder.container():
                if player_choice == computer_choice:
                    st.write("It's a tie!")
                elif (
                    (player_choice == "Rock" and computer_choice == "Scissors")
                    or (player_choice == "Scissors" and computer_choice == "Paper")
                    or (player_choice == "Paper" and computer_choice == "Rock")
                ):
                    st.write("You win this round!")
                    player_score += 1
                else:
                    st.write("Computer wins this round!")
                    computer_score += 1
                st.write(f"Your choice: **{player_choice}** | Computer's choice: **{computer_choice}**")
                st.write(f"Score: You {player_score} - {computer_score} Computer")
        
        # Display the frame with the placeholder
        frame_placeholder.image(frame, channels="BGR")

    # End of game
    st.write("---")
    if player_score == game_rounds:
        st.success(f"🎉 Congratulations! You won the game with a final score of {player_score} to {computer_score}!")
    elif computer_score == game_rounds:
        st.error(f"😭 The computer won the game with a final score of {computer_score} to {player_score}.")

    cap.release()
    cv2.destroyAllWindows()
