---
sidebar_label: 'Vision-Language-Action Examples'
---

# Vision-Language-Action Examples

## Overview
This section provides practical examples for implementing Vision-Language-Action (VLA) systems that integrate perception, language understanding, and action execution in humanoid robotics. These examples demonstrate how to connect visual scenes with natural language commands and appropriate robotic actions.

## Vision-Language Foundation Models

### CLIP-based Object Grounding
```python
import torch
import clip
from PIL import Image
import numpy as np
import cv2

class CLIPObjectGrounding:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model, self.preprocess = clip.load("ViT-B/32", device=device)

    def ground_object(self, image, text_queries):
        """
        Ground text queries in an image using CLIP
        Args:
            image: PIL Image or numpy array
            text_queries: List of text descriptions to ground
        Returns:
            List of probabilities for each text query
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        text_inputs = torch.cat([clip.tokenize(f"a photo of {q}") for q in text_queries]).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            text_features = self.model.encode_text(text_inputs)

            # Normalize features
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            # Calculate similarity
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            probs = similarity.cpu().numpy()[0]

        return probs

# Example usage
def example_clip_grounding():
    grounding = CLIPObjectGrounding()

    # Example: Find if image contains a red cup, blue book, or green plant
    image = Image.open("example_image.jpg")  # Replace with actual image
    queries = ["a red cup", "a blue book", "a green plant"]

    probabilities = grounding.ground_object(image, queries)

    for i, (query, prob) in enumerate(zip(queries, probabilities)):
        print(f"{query}: {prob:.2f}")
```

### Vision-Language Model Integration with ROS 2
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import torch
import clip
import numpy as np

class VisionLanguageNode(Node):
    def __init__(self):
        super().__init__('vision_language_node')

        # Initialize CLIP model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

        # Create subscribers and publishers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.command_sub = self.create_subscription(
            String, '/robot/command', self.command_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.bridge = CvBridge()
        self.current_image = None
        self.current_command = None

    def image_callback(self, msg):
        try:
            # Convert ROS image to PIL Image
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.current_image = Image.fromarray(cv_image[:, :, ::-1])  # Convert BGR to RGB
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def command_callback(self, msg):
        try:
            self.current_command = msg.data
            if self.current_image is not None:
                self.process_command()
        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')

    def process_command(self):
        if not self.current_command or not self.current_image:
            return

        # Example: Simple command processing
        command = self.current_command.lower()

        if "move to" in command or "go to" in command:
            # Extract object from command (simplified)
            object_name = command.split()[-1]  # Get last word as object

            # Ground the object in the image
            prob = self.ground_object_in_image(self.current_image, object_name)

            if prob > 0.5:  # If object likely present
                self.get_logger().info(f'Found {object_name} with probability {prob:.2f}')
                # Execute navigation to object
                self.navigate_to_object(object_name)
            else:
                self.get_logger().info(f'Did not find {object_name} in the scene')

    def ground_object_in_image(self, image, object_name):
        """Ground a specific object in the image using CLIP"""
        image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
        text_input = clip.tokenize([f"a photo of {object_name}", "a photo of background"]).to(self.device)

        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_input)
            text_features = self.clip_model.encode_text(text_input)

            # Normalize features
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            # Calculate similarity
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            object_prob = similarity.cpu().numpy()[0][0]  # Probability of object being present

        return object_prob

    def navigate_to_object(self, object_name):
        """Simple navigation command - in practice this would be more sophisticated"""
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.2  # Move forward slowly
        cmd_vel.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd_vel)
        self.get_logger().info(f'Navigating towards {object_name}')

def main(args=None):
    rclpy.init(args=args)
    node = VisionLanguageNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Language Processing for Robot Commands

### Natural Language Command Parser
```python
import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RobotCommand:
    action: str
    target: Optional[str] = None
    location: Optional[str] = None
    properties: dict = None

class CommandParser:
    def __init__(self):
        # Define action patterns
        self.action_patterns = {
            'move': [r'go to', r'move to', r'walk to', r'navigate to', r'approach'],
            'grasp': [r'pick up', r'grab', r'get', r'grasp', r'take'],
            'place': [r'put', r'place', r'set down', r'drop'],
            'follow': [r'follow', r'accompany', r'go with'],
            'inspect': [r'look at', r'inspect', r'examine', r'check'],
            'transport': [r'bring', r'carry to', r'deliver to']
        }

        # Location patterns
        self.location_patterns = [
            r'to the (\w+)', r'at the (\w+)', r'near the (\w+)', r'by the (\w+)',
            r'in the (\w+)', r'on the (\w+)', r'at (\w+)'
        ]

    def parse_command(self, text: str) -> Optional[RobotCommand]:
        text = text.lower().strip()

        # Extract action
        action = self._extract_action(text)
        if not action:
            return None

        # Extract target object
        target = self._extract_target(text, action)

        # Extract location
        location = self._extract_location(text)

        return RobotCommand(
            action=action,
            target=target,
            location=location,
            properties={}
        )

    def _extract_action(self, text: str) -> Optional[str]:
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return action
        return None

    def _extract_target(self, text: str, action: str) -> Optional[str]:
        # Simple extraction - in practice, use more sophisticated NLP
        # Remove action words to find target
        text_without_action = text
        for pattern in self.action_patterns[action]:
            text_without_action = re.sub(pattern, '', text_without_action)

        # Look for object descriptions
        words = text_without_action.split()
        # Filter out common words and keep potential objects
        potential_objects = [w for w in words if w not in ['the', 'a', 'an', 'and', 'or', 'then']]

        if potential_objects:
            return ' '.join(potential_objects[:2])  # Take first 1-2 words as target

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        for pattern in self.location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

# Example usage
def example_command_parsing():
    parser = CommandParser()

    commands = [
        "Please pick up the red cup and place it on the table",
        "Move to the kitchen and check the status",
        "Follow the person to the conference room",
        "Grasp the blue marker from the desk"
    ]

    for cmd in commands:
        parsed = parser.parse_command(cmd)
        if parsed:
            print(f"Command: {cmd}")
            print(f"  Action: {parsed.action}")
            print(f"  Target: {parsed.target}")
            print(f"  Location: {parsed.location}")
            print()
```

## Action Planning and Execution

### Simple Action Planner
```python
from enum import Enum
from typing import List, Dict, Any
import time

class ActionType(Enum):
    MOVE_TO = "move_to"
    GRASP = "grasp"
    PLACE = "place"
    INSPECT = "inspect"
    FOLLOW = "follow"
    TRANSPORT = "transport"

@dataclass
class Action:
    type: ActionType
    parameters: Dict[str, Any]
    duration: float = 0.0

class SimpleActionPlanner:
    def __init__(self):
        self.action_library = {
            ActionType.MOVE_TO: self._execute_move_to,
            ActionType.GRASP: self._execute_grasp,
            ActionType.PLACE: self._execute_place,
            ActionType.INSPECT: self._execute_inspect,
            ActionType.FOLLOW: self._execute_follow,
        }

    def plan_action_sequence(self, command: RobotCommand) -> List[Action]:
        """Plan a sequence of actions based on a high-level command"""
        actions = []

        if command.action == 'move':
            actions.append(Action(
                type=ActionType.MOVE_TO,
                parameters={'target': command.location or command.target}
            ))

        elif command.action == 'grasp':
            # Move to target first, then grasp
            actions.append(Action(
                type=ActionType.MOVE_TO,
                parameters={'target': command.target}
            ))
            actions.append(Action(
                type=ActionType.GRASP,
                parameters={'object': command.target}
            ))

        elif command.action == 'place':
            # This would typically follow a grasp action
            actions.append(Action(
                type=ActionType.PLACE,
                parameters={'location': command.location}
            ))

        elif command.action == 'transport':
            # Pick up object and move to location
            actions.append(Action(
                type=ActionType.GRASP,
                parameters={'object': command.target}
            ))
            actions.append(Action(
                type=ActionType.MOVE_TO,
                parameters={'target': command.location}
            ))
            actions.append(Action(
                type=ActionType.PLACE,
                parameters={'location': command.location}
            ))

        elif command.action == 'inspect':
            actions.append(Action(
                type=ActionType.MOVE_TO,
                parameters={'target': command.target}
            ))
            actions.append(Action(
                type=ActionType.INSPECT,
                parameters={'target': command.target}
            ))

        return actions

    def execute_action_sequence(self, actions: List[Action]):
        """Execute a sequence of actions"""
        for action in actions:
            self._execute_action(action)

    def _execute_action(self, action: Action):
        """Execute a single action"""
        self.get_logger().info(f'Executing action: {action.type.value} with parameters: {action.parameters}')

        # Look up execution function
        if action.type in self.action_library:
            execution_func = self.action_library[action.type]
            execution_func(action.parameters)
        else:
            self.get_logger().error(f'Unknown action type: {action.type}')

    def _execute_move_to(self, params: Dict[str, Any]):
        """Execute move to action"""
        target = params.get('target', 'unknown location')
        self.get_logger().info(f'Moving to {target}')
        # In practice, this would call navigation stack
        time.sleep(2)  # Simulate movement time

    def _execute_grasp(self, params: Dict[str, Any]):
        """Execute grasp action"""
        obj = params.get('object', 'unknown object')
        self.get_logger().info(f'Grasping {obj}')
        # In practice, this would call manipulation stack
        time.sleep(3)  # Simulate grasp time

    def _execute_place(self, params: Dict[str, Any]):
        """Execute place action"""
        location = params.get('location', 'unknown location')
        self.get_logger().info(f'Placing object at {location}')
        # In practice, this would call manipulation stack
        time.sleep(2)  # Simulate placement time

    def _execute_inspect(self, params: Dict[str, Any]):
        """Execute inspect action"""
        target = params.get('target', 'unknown target')
        self.get_logger().info(f'Inspecting {target}')
        # In practice, this would trigger perception pipeline
        time.sleep(2)  # Simulate inspection time

    def _execute_follow(self, params: Dict[str, Any]):
        """Execute follow action"""
        target = params.get('target', 'unknown target')
        self.get_logger().info(f'Following {target}')
        # In practice, this would call person following behavior
        time.sleep(1)  # Simulate start of following

# ROS 2 Node that integrates command parsing and action planning
class VLARobotController(Node):
    def __init__(self):
        super().__init__('vla_robot_controller')

        # Initialize components
        self.command_parser = CommandParser()
        self.action_planner = SimpleActionPlanner()

        # Create subscribers and publishers
        self.command_sub = self.create_subscription(
            String, '/robot/natural_command', self.command_callback, 10)
        self.status_pub = self.create_publisher(String, '/robot/status', 10)

    def command_callback(self, msg):
        try:
            # Parse the natural language command
            command = self.command_parser.parse_command(msg.data)
            if command:
                self.get_logger().info(f'Parsed command: {command}')

                # Plan action sequence
                action_sequence = self.action_planner.plan_action_sequence(command)
                self.get_logger().info(f'Planned {len(action_sequence)} actions')

                # Execute action sequence
                self.action_planner.execute_action_sequence(action_sequence)

                # Publish completion status
                status_msg = String()
                status_msg.data = f'Completed command: {msg.data}'
                self.status_pub.publish(status_msg)
            else:
                self.get_logger().error(f'Could not parse command: {msg.data}')

        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = VLARobotController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Vision-Language-Action Integration Example

### Complete VLA System
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import torch
import clip
from PIL import Image as PILImage
import numpy as np
import time

class VisionLanguageActionSystem(Node):
    def __init__(self):
        super().__init__('vla_system')

        # Initialize components
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
        self.bridge = CvBridge()

        # Current state
        self.current_image = None
        self.command_queue = []

        # Create subscribers and publishers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.command_sub = self.create_subscription(
            String, '/robot/vla_command', self.command_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/robot/vla_status', 10)

        # Timer for processing loop
        self.process_timer = self.create_timer(0.1, self.process_commands)

    def image_callback(self, msg):
        """Receive and store camera image"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.current_image = PILImage.fromarray(cv_image[:, :, ::-1])  # Convert BGR to RGB
            self.get_logger().debug('Received new image')
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def command_callback(self, msg):
        """Receive and queue VLA commands"""
        try:
            self.command_queue.append(msg.data)
            self.get_logger().info(f'Queued command: {msg.data}')
        except Exception as e:
            self.get_logger().error(f'Error queuing command: {e}')

    def process_commands(self):
        """Process commands in the queue"""
        if not self.command_queue or self.current_image is None:
            return

        command = self.command_queue.pop(0)
        self.get_logger().info(f'Processing command: {command}')

        # Update status
        status_msg = String()
        status_msg.data = f'Processing: {command}'
        self.status_pub.publish(status_msg)

        # Execute the VLA pipeline
        success = self.execute_vla_command(command)

        # Update final status
        final_status = String()
        final_status.data = f'Completed: {command}' if success else f'Failed: {command}'
        self.status_pub.publish(final_status)

    def execute_vla_command(self, command: str) -> bool:
        """Execute a Vision-Language-Action command"""
        try:
            # Step 1: Parse the command
            action, target = self.parse_command(command)
            if not action or not target:
                self.get_logger().error(f'Could not parse command: {command}')
                return False

            # Step 2: Ground the target in the current image
            target_probability = self.ground_target_in_image(target)
            self.get_logger().info(f'Target "{target}" probability: {target_probability:.2f}')

            if target_probability < 0.3:  # Threshold for target detection
                self.get_logger().error(f'Target "{target}" not found in scene')
                return False

            # Step 3: Execute the action
            if action == 'grasp':
                return self.execute_grasp(target)
            elif action == 'move_to':
                return self.execute_move_to(target)
            elif action == 'inspect':
                return self.execute_inspect(target)
            else:
                self.get_logger().error(f'Unknown action: {action}')
                return False

        except Exception as e:
            self.get_logger().error(f'Error executing VLA command: {e}')
            return False

    def parse_command(self, command: str):
        """Simple command parsing"""
        command_lower = command.lower()

        # Extract action
        if 'grasp' in command_lower or 'pick up' in command_lower or 'grab' in command_lower:
            action = 'grasp'
        elif 'move to' in command_lower or 'go to' in command_lower or 'approach' in command_lower:
            action = 'move_to'
        elif 'look at' in command_lower or 'inspect' in command_lower or 'examine' in command_lower:
            action = 'inspect'
        else:
            return None, None

        # Extract target (simplified)
        # In practice, use more sophisticated NLP
        words = command_lower.split()
        target_words = []
        for word in words:
            if word not in ['please', 'the', 'a', 'an', 'and', 'to', 'at', 'for', 'in', 'on', 'with']:
                target_words.append(word)

        if target_words:
            # Take the last 1-2 words as target
            target = ' '.join(target_words[-2:])
        else:
            return None, None

        return action, target

    def ground_target_in_image(self, target: str) -> float:
        """Ground the target object in the current image using CLIP"""
        if self.current_image is None:
            return 0.0

        try:
            image_input = self.clip_preprocess(self.current_image).unsqueeze(0).to(self.device)
            text_input = clip.tokenize([f"a photo of {target}", "a photo of background"]).to(self.device)

            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                text_features = self.clip_model.encode_text(text_input)

                # Normalize features
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)

                # Calculate similarity
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                target_prob = similarity.cpu().numpy()[0][0]

            return float(target_prob)

        except Exception as e:
            self.get_logger().error(f'Error in target grounding: {e}')
            return 0.0

    def execute_grasp(self, target: str) -> bool:
        """Execute grasp action"""
        self.get_logger().info(f'Executing grasp for {target}')

        # In practice, this would:
        # 1. Use perception to locate the object precisely
        # 2. Plan a grasping trajectory
        # 3. Execute the grasp with manipulator
        # 4. Verify success

        # Simulate the action
        time.sleep(3)  # Simulate grasp time

        # Publish command to move forward (simplified)
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.1  # Move forward slowly
        cmd_vel.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

        time.sleep(2)  # Simulate movement time

        # Stop
        cmd_vel.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

        return True  # Simulate success

    def execute_move_to(self, target: str) -> bool:
        """Execute move to action"""
        self.get_logger().info(f'Executing move to for {target}')

        # In practice, this would:
        # 1. Use navigation stack to plan path
        # 2. Execute path following
        # 3. Verify arrival at destination

        # Simulate the action
        time.sleep(2)  # Simulate planning time

        # Publish movement command (simplified)
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.2  # Move forward
        cmd_vel.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

        time.sleep(3)  # Simulate movement time

        # Stop
        cmd_vel.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

        return True  # Simulate success

    def execute_inspect(self, target: str) -> bool:
        """Execute inspect action"""
        self.get_logger().info(f'Executing inspect for {target}')

        # In practice, this would:
        # 1. Move to get a good view of the target
        # 2. Execute perception pipeline
        # 3. Process and analyze the data

        # Simulate the action
        time.sleep(2)  # Simulate movement for good view

        # Publish rotation command to look around (simplified)
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = 0.3  # Rotate slowly
        self.cmd_vel_pub.publish(cmd_vel)

        time.sleep(2)  # Simulate rotation time

        # Stop
        cmd_vel.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

        return True  # Simulate success

def main(args=None):
    rclpy.init(args=args)
    node = VisionLanguageActionSystem()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Advanced VLA Techniques

### Multi-Step Task Planning
```python
class MultiStepTaskPlanner:
    def __init__(self):
        self.knowledge_base = {
            'kitchen': ['cup', 'plate', 'fridge', 'counter'],
            'living_room': ['sofa', 'table', 'tv', 'remote'],
            'bedroom': ['bed', 'dresser', 'nightstand'],
            'office': ['desk', 'chair', 'computer', 'printer']
        }

    def plan_complex_task(self, command: str) -> List[Action]:
        """
        Plan complex tasks that may span multiple rooms or require
        object manipulation and navigation
        """
        # Example: "Go to the kitchen, pick up a cup, and bring it to the living room"
        actions = []

        if 'bring' in command.lower() or 'transport' in command.lower():
            # Extract source and destination
            source = self.extract_room(command, 'source')
            destination = self.extract_room(command, 'destination')
            object_to_transport = self.extract_object(command)

            if source and destination and object_to_transport:
                # 1. Go to source location
                actions.append(Action(
                    type=ActionType.MOVE_TO,
                    parameters={'target': source}
                ))

                # 2. Grasp the object
                actions.append(Action(
                    type=ActionType.GRASP,
                    parameters={'object': object_to_transport}
                ))

                # 3. Go to destination
                actions.append(Action(
                    type=ActionType.MOVE_TO,
                    parameters={'target': destination}
                ))

                # 4. Place the object
                actions.append(Action(
                    type=ActionType.PLACE,
                    parameters={'location': destination}
                ))

        return actions

    def extract_room(self, command: str, role: str) -> Optional[str]:
        """Extract room based on context"""
        command_lower = command.lower()

        # Look for location indicators
        if role == 'source':
            # Look for words indicating source
            for room in self.knowledge_base.keys():
                if f'from the {room}' in command_lower or f'at the {room}' in command_lower:
                    return room
        elif role == 'destination':
            # Look for words indicating destination
            for room in self.knowledge_base.keys():
                if f'to the {room}' in command_lower:
                    return room

        # If not found explicitly, try to infer
        if role == 'destination':
            # Destination is often at the end
            if 'living room' in command_lower:
                return 'living_room'
            elif 'kitchen' in command_lower:
                return 'kitchen'
            elif 'bedroom' in command_lower:
                return 'bedroom'
            elif 'office' in command_lower:
                return 'office'

        return None

    def extract_object(self, command: str) -> Optional[str]:
        """Extract object to manipulate"""
        command_lower = command.lower()

        # Look for common objects
        for room_objects in self.knowledge_base.values():
            for obj in room_objects:
                if obj in command_lower:
                    return obj

        # If not found in knowledge base, extract potential objects
        words = command_lower.split()
        potential_objects = [w for w in words if w not in
                           ['the', 'a', 'an', 'and', 'or', 'then', 'to', 'from', 'at', 'in', 'on']]

        if potential_objects:
            return potential_objects[0]  # Return first potential object

        return None
```

## Integration with Navigation and Manipulation

### Complete Integration Example
```python
class IntegratedVLASystem(Node):
    def __init__(self):
        super().__init__('integrated_vla_system')

        # Initialize components
        self.vision_system = CLIPObjectGrounding()
        self.command_parser = CommandParser()
        self.task_planner = MultiStepTaskPlanner()
        self.action_executor = SimpleActionPlanner()

        # ROS 2 interfaces
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.command_sub = self.create_subscription(
            String, '/high_level_command', self.command_callback, 10)
        self.status_pub = self.create_publisher(String, '/vla_system_status', 10)

        self.current_image = None
        self.command_queue = []

    def image_callback(self, msg):
        """Process incoming images"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.current_image = PILImage.fromarray(cv_image[:, :, ::-1])
        except Exception as e:
            self.get_logger().error(f'Image processing error: {e}')

    def command_callback(self, msg):
        """Process high-level commands"""
        try:
            # Parse command
            robot_command = self.command_parser.parse_command(msg.data)
            if robot_command:
                # Plan task
                action_sequence = self.task_planner.plan_complex_task(msg.data)

                # Execute or queue for execution
                if action_sequence:
                    self.execute_action_sequence(action_sequence)
                else:
                    self.get_logger().error(f'Could not plan task for: {msg.data}')
            else:
                self.get_logger().error(f'Could not parse command: {msg.data}')

        except Exception as e:
            self.get_logger().error(f'Command processing error: {e}')

    def execute_action_sequence(self, actions: List[Action]):
        """Execute a sequence of actions safely"""
        for action in actions:
            try:
                success = self.execute_single_action(action)
                if not success:
                    self.get_logger().error(f'Action failed: {action}')
                    break  # Stop execution if action fails
            except Exception as e:
                self.get_logger().error(f'Action execution error: {e}')
                break

def main(args=None):
    rclpy.init(args=args)
    node = IntegratedVLASystem()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices Summary

### Vision Components
- Use pre-trained models like CLIP for zero-shot object grounding
- Implement efficient preprocessing pipelines
- Consider computational constraints for real-time operation
- Validate visual grounding with multiple modalities when possible

### Language Understanding
- Implement robust command parsing with error handling
- Use context-aware language models when available
- Design for ambiguous or incomplete commands
- Provide feedback to users about command interpretation

### Action Execution
- Plan multi-step tasks considering robot capabilities
- Implement safety checks before executing actions
- Provide feedback during action execution
- Handle failures gracefully with recovery strategies

### Integration
- Design modular components that can be tested independently
- Implement proper state management for complex tasks
- Use appropriate communication patterns between components
- Design for scalability to handle multiple concurrent tasks

These examples demonstrate how to build complete Vision-Language-Action systems that enable natural human-robot interaction. Each component can be extended and customized based on specific application requirements.