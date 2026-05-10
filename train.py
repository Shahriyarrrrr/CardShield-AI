from ultralytics import YOLO
from multiprocessing import freeze_support

def main():
    model = YOLO("yolov8n.pt")

    model.train(
        data="dataset/card.yaml",
        epochs=25,
        imgsz=640,
        batch=8,
        workers=0,
        device=0
    )

if __name__ == "__main__":
    freeze_support()
    main()