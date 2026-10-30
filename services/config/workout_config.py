Exercise_options = [
    "Squats",
    "Push-up",
    "Burpees",
    "Pull-ups",
    "Lunges",
    "Leg-Raises",
 
]
TIMED_EXERCISES = {"Jumping Jack", "Planks", "Mountain climbers"}

POSE_CONNECTIONS = [   #lines for detection
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),       # Shoulders & Arms
    (11, 23), (12, 24), (23, 24),                           # Torso / Hips
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)  # Legs
]

METRICS_FIELDS = {
    "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },
    "Push-up": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },
    "Burpees": {
        "hip_angle": 0,
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "composite_movement": "N/A",
    },
    "Pull-ups": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },
    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },
    "Planks": {
        "back_angle": 0,
        "hip_angle": 0,
        "body_alignment": "N/A",
    },
    "Jumping Jack": {
        "shoulder_angle": 0,
        "swing_status": "N/A",
        "composite_movement": "N/A",
    },
    "Mountain climbers": {
        "knee_angle": 0,
        "hip_angle": 0,
        "torso_angle": 0,
        "composite_movement": "N/A",
    },
    "Leg-Raises": {
        "hip_angle": 0,
        "torso_angle": 0,
        "extension_status": "N/A",
    },
}