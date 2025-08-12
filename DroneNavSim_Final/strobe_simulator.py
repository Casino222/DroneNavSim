import os
import cv2
import numpy as np

def generate_sos_pattern(output_dir, frame_size=(100, 100), on_color=(255, 255, 255), off_color=(0, 0, 0)):
    os.makedirs(output_dir, exist_ok=True)
    pattern = [1]*15 + [0]*10 + [1]*30
    for i, val in enumerate(pattern):
        frame = np.full((frame_size[1], frame_size[0], 3), on_color if val else off_color, dtype=np.uint8)
        cv2.imwrite(os.path.join(output_dir, f"frame_{i:03d}.png"), frame)

if __name__ == "__main__":
    output_path = "assets/sos_sequence"
    generate_sos_pattern(output_path)
    print(f"✅ Saved {len(os.listdir(output_path))} SOS frames to {output_path}")