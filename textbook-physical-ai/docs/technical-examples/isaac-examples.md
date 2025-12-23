---
sidebar_label: 'NVIDIA Isaac Examples'
---

# NVIDIA Isaac Examples

## Overview
This section provides practical examples for implementing various features using the NVIDIA Isaac™ platform. These examples cover Isaac ROS packages, Isaac Sim usage, perception systems, and AI integration for humanoid robotics applications.

## Isaac ROS Examples

### Hardware-Accelerated Stereo Disparity
```python
import rclpy
from rclpy.node import Node
from stereo_msgs.msg import DisparityImage
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import cv2

class IsaacStereoNode(Node):
    def __init__(self):
        super().__init__('isaac_stereo_node')

        # Create publisher for disparity image
        self.disparity_pub = self.create_publisher(DisparityImage, 'disparity', 10)

        # Create subscribers for left and right camera images
        self.left_sub = self.create_subscription(
            Image, 'left/image_rect', self.left_callback, 10)
        self.right_sub = self.create_subscription(
            Image, 'right/image_rect', self.right_callback, 10)

        self.bridge = CvBridge()
        self.left_image = None
        self.right_image = None

    def left_callback(self, msg):
        try:
            self.left_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f'Error converting left image: {e}')

    def right_callback(self, msg):
        try:
            self.right_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            if self.left_image is not None:
                self.compute_disparity()
        except Exception as e:
            self.get_logger().error(f'Error converting right image: {e}')

    def compute_disparity(self):
        # Convert to grayscale
        left_gray = cv2.cvtColor(self.left_image, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(self.right_image, cv2.COLOR_BGR2GRAY)

        # Create stereo matcher (using SGBM as an example)
        stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=64,
            blockSize=5,
            P1=8 * 3 * 5**2,
            P2=32 * 3 * 5**2,
            disp12MaxDiff=1,
            uniquenessRatio=15,
            speckleWindowSize=0,
            speckleRange=2,
            preFilterCap=63,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        )

        # Compute disparity
        disparity = stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0

        # Create disparity message
        disp_msg = DisparityImage()
        disp_msg.header = self.left_sub._current_header
        disp_msg.image = self.bridge.cv2_to_imgmsg(disparity, "32FC1")
        disp_msg.f = 320.0  # Focal length (example value)
        disp_msg.T = 0.1  # Baseline (example value)

        self.disparity_pub.publish(disp_msg)

def main(args=None):
    rclpy.init(args=args)
    node = IsaacStereoNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Isaac ROS Image Pipeline Example
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import cv2
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose

class IsaacPerceptionNode(Node):
    def __init__(self):
        super().__init__('isaac_perception_node')

        # Create subscriber for camera image
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)

        # Create publisher for detections
        self.detection_pub = self.create_publisher(
            Detection2DArray, 'detections', 10)

        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Perform object detection (using a simple example)
            detections = self.detect_objects(cv_image)

            # Publish detections
            self.publish_detections(detections, msg.header)

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def detect_objects(self, image):
        # Example: Simple color-based detection
        # In practice, this would use a trained model
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Detect red objects
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        mask = mask1 + mask2

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                detection = Detection2D()
                detection.bbox.center.x = x + w/2
                detection.bbox.center.y = y + h/2
                detection.bbox.size_x = w
                detection.bbox.size_y = h

                # Add confidence score
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.hypothesis.class_id = "red_object"
                hypothesis.hypothesis.score = 0.8
                detection.results.append(hypothesis)

                detections.append(detection)

        return detections

    def publish_detections(self, detections, header):
        detection_array = Detection2DArray()
        detection_array.header = header
        detection_array.detections = detections
        self.detection_pub.publish(detection_array)

def main(args=None):
    rclpy.init(args=args)
    node = IsaacPerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Isaac Sim Python API Examples

### Creating a Simple Scene
```python
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.objects import DynamicCuboid
import numpy as np

# Initialize the world
my_world = World(stage_units_in_meters=1.0)

# Add a ground plane
my_world.scene.add_default_ground_plane()

# Add a robot (using a simple cuboid as example)
cube = my_world.scene.add(
    DynamicCuboid(
        prim_path="/World/cube",
        name="cube",
        position=np.array([0, 0, 1.0]),
        size=np.array([0.5, 0.5, 0.5]),
        mass=1.0
    )
)

# Add an object to manipulate
object_to_grab = my_world.scene.add(
    DynamicCuboid(
        prim_path="/World/object",
        name="object_to_grab",
        position=np.array([0.5, 0, 0.5]),
        size=np.array([0.1, 0.1, 0.1]),
        mass=0.1
    )
)

# Simulate for a few steps
for i in range(100):
    my_world.step(render=True)

my_world.reset()
```

### Robot Control in Isaac Sim
```python
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.types import ArticulationAction
import numpy as np

# Initialize the world
my_world = World(stage_units_in_meters=1.0)

# Get the robot asset path
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    print("Could not find Isaac Sim assets. Please enable Isaac Sim Nucleus.")
else:
    # Add a simple robot
    add_reference_to_stage(
        usd_path=assets_root_path + "/Isaac/Robots/Franka/franka.usd",
        prim_path="/World/Franka"
    )

    # Create robot object
    my_robot = Robot(
        prim_path="/World/Franka",
        name="franka_robot",
        position=np.array([0, 0, 0])
    )
    my_world.scene.add(my_robot)

    # Add a ground plane
    my_world.scene.add_default_ground_plane()

    # Reset the world
    my_world.reset()

    # Control the robot
    while simulation_app.is_running():
        my_world.step(render=True)

        if my_world.is_playing():
            # Get current joint positions
            joint_positions = my_robot.get_joint_positions()

            # Define target joint positions (example)
            target_positions = np.array([0.0, -1.0, 0.0, 2.0, 0.0, 0.5, 0.0])

            # Apply joint position commands
            my_robot.set_joint_position_targets(positions=target_positions)
```

## Isaac AI Integration Examples

### TensorRT Inference with Isaac
```python
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import cv2

class IsaacTensorRTInference:
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.engine = self.load_engine()
        self.context = self.engine.create_execution_context()
        self.setup_buffers()

    def load_engine(self):
        with open(self.engine_path, 'rb') as f:
            serialized_engine = f.read()

        runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
        engine = runtime.deserialize_cuda_engine(serialized_engine)
        return engine

    def setup_buffers(self):
        # Allocate host and device buffers
        self.host_inputs = []
        self.host_outputs = []
        self.cuda_inputs = []
        self.cuda_outputs = []
        self.bindings = []

        for idx in range(self.engine.num_bindings):
            print(f"Binding {idx}: {self.engine.get_binding_name(idx)}")
            print(f"Binding shape: {self.engine.get_binding_shape(idx)}")

            binding = self.engine.get_binding_name(idx)
            size = trt.volume(self.engine.get_binding_shape(idx)) * self.engine.max_batch_size * np.dtype(np.float32).itemsize
            host_mem = cuda.pagelocked_empty(size, np.float32)
            cuda_mem = cuda.mem_alloc(host_mem.nbytes)

            self.bindings.append(int(cuda_mem))

            if self.engine.binding_is_input(idx):
                self.host_inputs.append(host_mem)
                self.cuda_inputs.append(cuda_mem)
            else:
                self.host_outputs.append(host_mem)
                self.cuda_outputs.append(cuda_mem)

    def infer(self, input_data):
        # Copy input data to host buffer
        np.copyto(self.host_inputs[0], input_data.ravel())

        # Transfer input data to GPU
        cuda.memcpy_htod(self.cuda_inputs[0], self.host_inputs[0])

        # Execute inference
        self.context.execute_v2(bindings=self.bindings)

        # Transfer predictions back from GPU
        cuda.memcpy_dtoh(self.host_outputs[0], self.cuda_outputs[0])

        # Return output
        return self.host_outputs[0][:self.engine.get_binding_shape(1)[1]]

# Example usage in a ROS 2 node
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class IsaacAIPerceptionNode(Node):
    def __init__(self):
        super().__init__('isaac_ai_perception')

        # Initialize TensorRT inference
        self.inference = IsaacTensorRTInference('/path/to/model.engine')

        # Create subscriber and publisher
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)
        self.result_pub = self.create_publisher(
            Image, 'ai_result', 10)

        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Preprocess image for inference
            processed_image = self.preprocess_image(cv_image)

            # Run inference
            result = self.inference.infer(processed_image)

            # Process results
            annotated_image = self.annotate_image(cv_image, result)

            # Publish result
            result_msg = self.bridge.cv2_to_imgmsg(annotated_image, "bgr8")
            result_msg.header = msg.header
            self.result_pub.publish(result_msg)

        except Exception as e:
            self.get_logger().error(f'Error in AI perception: {e}')

    def preprocess_image(self, image):
        # Resize and normalize image
        resized = cv2.resize(image, (224, 224))
        normalized = resized.astype(np.float32) / 255.0
        # Transpose to CHW format
        transposed = np.transpose(normalized, (2, 0, 1))
        return transposed

    def annotate_image(self, image, results):
        # Draw results on image (example)
        annotated = image.copy()
        # Add your annotation logic here based on results
        return annotated

def main(args=None):
    rclpy.init(args=args)
    node = IsaacAIPerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Isaac Lab Example - Reinforcement Learning Environment

```python
# Example of using Isaac Lab for reinforcement learning
from omni.isaac.orbit_tasks.utils import parse_env_cfg
from omni.isaac.orbit_tasks.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg
from omni.isaac.orbit.assets import AssetBase
from omni.isaac.orbit.envs import ManagerBasedRLEnv
import torch

class IsaacLabExample:
    def __init__(self):
        # Parse environment configuration
        env_cfg = parse_env_cfg(
            "Isaac-Velocity-Flat-Anymal-D-v0",
            device="cuda:0",
            num_envs=64,  # Number of parallel environments
            use_fabric=True,
        )

        # Modify configuration as needed
        env_cfg.scene.num_envs = 64
        env_cfg.terminations.time_out = True

        # Create environment
        self.env = ManagerBasedRLEnv(cfg=env_cfg)

    def run_training_loop(self):
        # Reset environment
        obs_dict, _ = self.env.reset()

        for _ in range(1000):  # Training steps
            # Get random actions (in real training, this would be from policy)
            actions = torch.randn_like(self.env.action_manager.action)

            # Apply actions and get observations
            obs_dict, rews, terminated, truncated, infos = self.env.step(actions)

            # In a real training loop, you would update your policy here
            # For this example, we just continue

        self.env.close()

# Example usage
def main():
    example = IsaacLabExample()
    example.run_training_loop()

if __name__ == "__main__":
    main()
```

## Isaac ROS Bridge Example

### Creating Isaac ROS Package
```python
# Example of creating a custom Isaac ROS package
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from cv_bridge import CvBridge
import numpy as np
import cv2

class IsaacCustomNode(Node):
    def __init__(self):
        super().__init__('isaac_custom_node')

        # Create subscribers
        self.left_image_sub = self.create_subscription(
            Image, '/camera/left/image_rect_color', self.left_image_callback, 10)
        self.right_image_sub = self.create_subscription(
            Image, '/camera/right/image_rect_color', self.right_image_callback, 10)
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        # Create publishers
        self.disparity_pub = self.create_publisher(
            Image, '/disparity', 10)
        self.depth_pub = self.create_publisher(
            Image, '/depth', 10)
        self.processing_time_pub = self.create_publisher(
            Float32, '/processing_time', 10)

        self.bridge = CvBridge()
        self.left_image = None
        self.right_image = None

        # Stereo processing parameters
        self.stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=64,
            blockSize=5,
            P1=8 * 3 * 5**2,
            P2=32 * 3 * 5**2,
            disp12MaxDiff=1,
            uniquenessRatio=15,
            speckleWindowSize=0,
            speckleRange=2,
            preFilterCap=63,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        )

    def left_image_callback(self, msg):
        try:
            self.left_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            if self.right_image is not None:
                self.process_stereo()
        except Exception as e:
            self.get_logger().error(f'Error processing left image: {e}')

    def right_image_callback(self, msg):
        try:
            self.right_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            if self.left_image is not None:
                self.process_stereo()
        except Exception as e:
            self.get_logger().error(f'Error processing right image: {e}')

    def cmd_vel_callback(self, msg):
        # Process velocity commands
        linear_vel = msg.linear.x
        angular_vel = msg.angular.z
        self.get_logger().info(f'Received cmd_vel: linear={linear_vel}, angular={angular_vel}')

    def process_stereo(self):
        import time
        start_time = time.time()

        # Convert to grayscale
        left_gray = cv2.cvtColor(self.left_image, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(self.right_image, cv2.COLOR_BGR2GRAY)

        # Compute disparity
        disparity = self.stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0

        # Convert disparity to depth (simplified)
        # In practice, you would use proper camera calibration parameters
        baseline = 0.1  # Example baseline in meters
        focal_length = 320  # Example focal length in pixels
        depth = (baseline * focal_length) / (disparity + 1e-6)  # Add small value to avoid division by zero
        depth[depth > 100] = 0  # Set far distances to 0

        # Publish disparity image
        disparity_msg = self.bridge.cv2_to_imgmsg(disparity, "32FC1")
        disparity_msg.header = self.left_image_sub._current_header
        self.disparity_pub.publish(disparity_msg)

        # Publish depth image
        depth_msg = self.bridge.cv2_to_imgmsg(depth, "32FC1")
        depth_msg.header = self.left_image_sub._current_header
        self.depth_pub.publish(depth_msg)

        # Publish processing time
        processing_time = Float32()
        processing_time.data = time.time() - start_time
        self.processing_time_pub.publish(processing_time)

def main(args=None):
    rclpy.init(args=args)
    node = IsaacCustomNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Isaac Platform Integration Example

### Complete System Integration
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan, Imu
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np
import cv2

class IsaacIntegratedSystem(Node):
    def __init__(self):
        super().__init__('isaac_integrated_system')

        # Initialize bridge
        self.bridge = CvBridge()

        # Subscribers for various sensors
        self.camera_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.camera_callback, 10)
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)

        # Publishers for commands and processed data
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.nav_goal_pub = self.create_publisher(PoseStamped, '/move_base_simple/goal', 10)
        self.status_pub = self.create_publisher(String, '/system_status', 10)

        # System state
        self.current_pose = None
        self.lidar_data = None
        self.imu_data = None
        self.last_camera_time = None

        # Create timer for main control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)

    def camera_callback(self, msg):
        try:
            # Process camera data
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.last_camera_time = msg.header.stamp

            # Perform vision processing (example: simple motion detection)
            processed_result = self.process_vision(cv_image)

            # In a real system, this would trigger higher-level behaviors
            self.get_logger().debug('Processed camera image')

        except Exception as e:
            self.get_logger().error(f'Error processing camera: {e}')

    def lidar_callback(self, msg):
        try:
            # Store lidar data
            self.lidar_data = msg.ranges
            self.lidar_time = msg.header.stamp

            # Check for obstacles
            if self.lidar_data:
                min_range = min([r for r in self.lidar_data if r > msg.range_min and r < msg.range_max], default=float('inf'))
                if min_range < 1.0:  # Obstacle within 1 meter
                    self.get_logger().info(f'Obstacle detected at {min_range:.2f}m')

        except Exception as e:
            self.get_logger().error(f'Error processing lidar: {e}')

    def imu_callback(self, msg):
        try:
            # Store IMU data
            self.imu_data = {
                'orientation': [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w],
                'angular_velocity': [msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z],
                'linear_acceleration': [msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]
            }

        except Exception as e:
            self.get_logger().error(f'Error processing IMU: {e}')

    def odom_callback(self, msg):
        try:
            # Store odometry data
            self.current_pose = {
                'position': [msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z],
                'orientation': [msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w]
            }

        except Exception as e:
            self.get_logger().error(f'Error processing odometry: {e}')

    def process_vision(self, image):
        # Example vision processing function
        # In a real system, this might include object detection, SLAM, etc.

        # Simple example: detect color blobs
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define range for red color
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        mask = mask1 + mask2

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Return simple result
        return len(contours) > 0  # True if red object detected

    def control_loop(self):
        # Main control loop that integrates all sensor data
        cmd_vel = Twist()

        # Example behavior: stop if obstacle detected, otherwise move forward
        if self.lidar_data:
            min_range = min([r for r in self.lidar_data if r > 0.1 and r < 10.0], default=float('inf'))
            if min_range < 0.8:  # Stop if obstacle closer than 0.8m
                cmd_vel.linear.x = 0.0
                cmd_vel.angular.z = 0.0
            else:
                cmd_vel.linear.x = 0.3  # Move forward at 0.3 m/s
                cmd_vel.angular.z = 0.0
        else:
            # If no lidar data, stop
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0

        # Publish command
        self.cmd_vel_pub.publish(cmd_vel)

        # Publish system status
        status_msg = String()
        status_msg.data = f"Running - Pose: {self.current_pose is not None}, Sensors: Cam={self.last_camera_time is not None}, Lidar={self.lidar_data is not None}"
        self.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)
    node = IsaacIntegratedSystem()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices Summary

### Performance Optimization
- Use Isaac ROS packages for hardware-accelerated processing
- Optimize TensorRT models for your specific hardware
- Implement efficient memory management in simulation
- Use appropriate update rates for different components

### Safety and Reliability
- Implement proper error handling and fallback behaviors
- Use safety limits and constraints in control systems
- Validate simulation results against real-world data
- Design for graceful degradation when components fail

### Integration
- Follow ROS 2 best practices for message passing
- Use Isaac-specific tools for perception and control
- Implement proper calibration between simulation and reality
- Design modular systems that can be tested independently

### Development Workflow
- Use Isaac Sim for rapid prototyping and testing
- Implement iterative development with simulation validation
- Use Isaac Lab for advanced learning-based approaches
- Document and version control your simulation environments

These examples demonstrate the key capabilities of the NVIDIA Isaac™ platform for developing intelligent robotic systems. Each example can be extended and combined to create sophisticated humanoid robot applications.