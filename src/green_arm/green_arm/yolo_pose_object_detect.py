import os
import rclpy
import cv2
from rclpy.node import Node
from ultralytics import YOLO
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
from ament_index_python.packages import get_package_share_directory

class YOLO_ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector_node')

        # Parameters
        default_model_path = os.path.join(get_package_share_directory('green_arm'), 'yolov8n.pt')
        self.declare_parameter("model", default_model_path)
        model_path = self.get_parameter("model").get_parameter_value().string_value

        self.declare_parameter("device", "cpu")
        self._device = self.get_parameter("device").get_parameter_value().string_value

        self.declare_parameter("threshold", 0.5)
        self._threshold = self.get_parameter("threshold").get_parameter_value().double_value

        self.declare_parameter("camera_topic", "/mycamera/image_raw")
        self._camera_topic = self.get_parameter("camera_topic").get_parameter_value().string_value

        # Model and bridge
        self._bridge = CvBridge()
        self._model = YOLO(model_path)
        self._model.fuse()

        # Subscriber
        self._sub = self.create_subscription(Image, self._camera_topic, self._camera_callback, qos_profile_sensor_data)

    def _camera_callback(self, data):
        self.get_logger().info(f'{self.get_name()} received image')
        img = self._bridge.imgmsg_to_cv2(data)

        results = self._model.predict(
            source=img,
            verbose=False,
            stream=False,
            conf=self._threshold,
            device=self._device
        )

        if not results or len(results[0].boxes) == 0:
            self.get_logger().info(f'{self.get_name()} no objects detected')
            return

        result = results[0].cpu()
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = self._model.names[cls_id]
            self.get_logger().info(f'Detected: {label} ({conf:.2f})')

        # Visualize results
        annotated_frame = result.plot()
        cv2.imshow('Detected Objects', annotated_frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = YOLO_ObjectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
