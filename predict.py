from ultralytics import YOLO

model = YOLO(
    "runs/detect/train-5/weights/best.pt"
)

results = model.predict(
    source="dataset/images/test",
    save=True,
    conf=0.25
)

print("Prediction completed.")
source="dataset/images/val"