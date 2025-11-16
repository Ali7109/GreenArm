from ultralytics import YOLO

model = YOLO('ODv4.pt')
results = model.predict('far.jpg', show=True)