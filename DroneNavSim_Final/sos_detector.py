import pickle
import cv2
import numpy as np
import os

def load_model(model_path='models/sos_classifier.pkl'):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def get_brightness_sequence(folder='assets/sos_sequence'):
    brightness_values = []
    for i in range(60):
        img_path = os.path.join(folder, f'frame_{i:03}.png')
        if not os.path.exists(img_path):
            continue
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        brightness = np.mean(img)
        brightness_values.append(brightness)
    return brightness_values

def detect_sos_pattern():
    model = load_model()
    brightness_values = get_brightness_sequence()
    if len(brightness_values) != 60:
        return False, 0.0  # Incomplete sequence
    prediction = model.predict([brightness_values])[0]
    confidence = model.predict_proba([brightness_values])[0][prediction] if hasattr(model, "predict_proba") else 1.0
    return bool(prediction), confidence

# Only show output when run directly
if __name__ == "__main__":
    found, confidence = detect_sos_pattern()
    if found:
        print(f"✅ SOS pattern detected by AI model! (Confidence: {confidence:.2f})")
    else:
        print("❌ No SOS pattern detected.")
