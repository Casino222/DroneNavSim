
# DroneNavSim: Search and Rescue Drone Simulation

## Overview
**DroneNavSim** is an interactive simulation tool designed to model search-and-rescue operations using drones in both 2D and 3D environments. 
It includes:
- **Autonomous drone pathfinding** using the A* algorithm
- **Manual drone control** via keyboard (with live path trail)
- **SOS flash pattern detection** using AI-powered brightness analysis
- Random terrain and target generation for replayability
- 3D Panda3D simulation with terrain, trees, and drone models
- Real-time visualization of SOS signal detection and frame brightness

---

## Project Structure
```
DroneNavSim_Final/
├── drone_sim_3d_panda.py        # Panda3D 3D drone simulation
├── models/                      # 3D model assets (.egg, .bam)
│   ├── quadplane.egg
│   ├── sos_classifier.pkl
│   ├── envir-ground.jpg
│   ├── environment.egg
│   ├── envir-tree2.png
│   ├──rgbCube.egg
├── drone_nav_simulator_auto.py  # Autonomous 2D simulation with A* pathfinding
├── terrain_generator.py         # Random terrain generator with obstacles
├── pathfinding.py               # A* search algorithm logic
├── strobe_simulator.py          # Generates SOS signal frames (full-frame flashes)
├── sos_detector.py              # AI-powered SOS detection with brightness visualization
├── ui/
│   ├── manual_gui.py            # Manual 2D drone navigation with live trail + legend
│   └── integrated_gui.py        # Manual 2D drone + SOS AI detection
├── assets/
│   └── sos_sequence/            # Frame-by-frame SOS strobe image sequence
└── README.md
```

---

## 🚀 How to Use

### 🧠 Autonomous Navigation
Simulate a drone flying to a randomized goal using A*:
```bash
python drone_nav_simulator_auto.py
```

### 🎮 Manual Drone Control
Use WASD to move and leave a visible trail.
```bash
python ui/manual_gui.py
```

### 🎯 Integrated Drone + SOS AI
Manually fly and detect an in-grid SOS signal using real-time AI:
```bash
python ui/integrated_gui.py
```

### 🔦 Generate SOS Flash Sequence
Generate an SOS Morse code signal as 60 full-frame white/black images:
```bash
python strobe_simulator.py
```

### 🧠 Run AI SOS Detection
Detect SOS in the generated frames and visualize brightness:
```bash
python sos_detector.py
```

---

## 🎛️ Manual Mode Controls

| Key | Action                |
|-----|-----------------------|
| W   | Move Up               |
| S   | Move Down             |
| A   | Move Left             |
| D   | Move Right            |


---

## 🧠 AI Detection Model

- **Type**: Random Forest Classifier
- **Input**: 60-frame brightness sequence
- **Accuracy**: ~97.5% (synthetically trained)
- **Output**: SOS detection with confidence score

---

## 🔧 Dependencies

- Python 3.8+
- `pygame`
- `opencv-python`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `joblib`
- `panda3d`

Install everything:
```bash
pip install pygame opencv-python numpy matplotlib scikit-learn joblib panda3d

```

---

## 🧩 Future Enhancements

- Live webcam SOS detection with OpenCV
- Multi-drone swarm support
- Terrain persistence and mission logs
- GUI toggle between AI/manual/autonomous modes
- Confidence threshold calibration


---

## 👨‍💻 Author
Developed by Matt Brownlee 
