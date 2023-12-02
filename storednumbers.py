import cv2
import inference
import supervision as sv
from collections import Counter

annotator = sv.BoxAnnotator()

# List to store detected card numbers
detected_card_numbers = []


def extract_card_numbers(labels):
    # Assuming labels contain card numbers
    # Modify this based on the actual structure of your labels
    card_numbers = []

    for label in labels:
        try:
            # Attempt to convert the label to an integer
            card_number = int(label)
            card_numbers.append(card_number)
        except ValueError:
            # Handle non-numeric labels (e.g., 'A' for Ace)
            if label.upper() == 'A':
                # For 'A', consider both 1 and 11
                card_numbers.extend([1, 11])
            # Add more conditions if needed for other non-numeric labels
            if label.upper() == 'K':
                # For 'A', consider both 1 and 11
                card_numbers.extend([10])
            if label.upper() == 'Q':
                # For 'A', consider both 1 and 11
                card_numbers.extend([10])
            if label.upper() == 'J':
                # For 'A', consider both 1 and 11
                card_numbers.extend([10])

    return card_numbers


def decide_hit_or_stand(card_numbers):
    # Assuming card_numbers is a list of integers representing the card values
    hand_value = sum(card_numbers)

    # Adjust this threshold based on your strategy
    hit_threshold = 16

    if hand_value < hit_threshold:
        return "Hit"
    else:
        return "Stand"


def on_prediction(predictions, image):
    labels = [p["class"] for p in predictions["predictions"]]
    detections = sv.Detections.from_roboflow(predictions)

    # Extract card numbers
    card_numbers = extract_card_numbers(labels)

    # Update detected card numbers
    detected_card_numbers.extend(card_numbers)

    # Get the two most common card numbers
    counter = Counter(detected_card_numbers)
    most_common_numbers = counter.most_common(2)
    most_common_card_numbers = [
        number for number, count in most_common_numbers]

    # Display the detected card numbers as text
    text_display = "Detected Card Numbers: {}".format(
        ", ".join(map(str, most_common_card_numbers)))
    cv2.putText(image, text_display, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Make decision based on card numbers
    decision = decide_hit_or_stand(most_common_card_numbers)
    decision_text = "Decision: {}".format(decision)
    cv2.putText(image, decision_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Print detected card numbers and decision to the console
    print("Detected Card Numbers:", most_common_card_numbers)
    print(decision)

    # Annotate and display the image
    annotated_image = annotator.annotate(
        scene=image,
        detections=detections,
        labels=labels
    )
    cv2.imshow("Prediction", annotated_image)
    cv2.waitKey(1)


# Rest of your code remains unchanged
inference.Stream(
    source="webcam",
    model="card-detection-number-only/1",
    output_channel_order="BGR",
    use_main_thread=True,
    api_key="J0ExVpm7IZ7D7dQ02N7D",
    on_prediction=on_prediction,
)
