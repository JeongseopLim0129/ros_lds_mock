import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math
import random

# 상수 정의
ANGLE_MIN_DEG = 0
ANGLE_MAX_DEG = 359
ANGLE_INCREMENT_DEG = 1
NUM_POINTS = 360
RANGE_MIN = 0.12
RANGE_MAX = 3.5

class MockScanPublisher(Node):
    def __init__(self):
        super().__init__('mock_scan_publisher')
        
        self.publisher_ = self.create_publisher(LaserScan, 'scan', 10)
        
        self.timer = self.create_timer(2.0, self.timer_callback)
        
        self.available_patterns = ["front_wall", "left_wall", "right_wall", "empty"]
        self.get_logger().info('Mock LaserScan Publisher Started')

    def timer_callback(self):
        pattern_name = random.choice(self.available_patterns)
        
        scan_msg = self.generate_scan_msg(pattern_name)
        
        self.publisher_.publish(scan_msg)
        self.get_logger().info(f'Published Scan: {pattern_name}')

    def create_base_scan(self):
        scan = LaserScan()
        
        scan.header.frame_id = 'laser_frame'
        scan.header.stamp = self.get_clock().now().to_msg()
        
        scan.angle_min = math.radians(ANGLE_MIN_DEG)
        scan.angle_max = math.radians(ANGLE_MAX_DEG)
        scan.angle_increment = math.radians(ANGLE_INCREMENT_DEG)
        
        scan.time_increment = 0.0
        scan.scan_time = 0.0
        
        scan.range_min = RANGE_MIN
        scan.range_max = RANGE_MAX
        
        scan.ranges = [float(RANGE_MAX) for _ in range(NUM_POINTS)]
        scan.intensities = [100.0 for _ in range(NUM_POINTS)]
        
        return scan

    def make_the_wall(self, ranges, center_deg, width_deg):
        half_width = width_deg // 2
        for offset in range(-half_width, half_width + 1):
            idx = (center_deg + offset) % NUM_POINTS
            ranges[idx] = 0.4

    def generate_scan_msg(self, pattern_name):
        scan = self.create_base_scan()
        
        if pattern_name == "front_wall":
            self.make_the_wall(scan.ranges, center_deg=0, width_deg=40)
            
        elif pattern_name == "left_wall":
            self.make_the_wall(scan.ranges, center_deg=0, width_deg=40)
            self.make_the_wall(scan.ranges, center_deg=90, width_deg=30)
            
        elif pattern_name == "right_wall":
            self.make_the_wall(scan.ranges, center_deg=0, width_deg=40)
            self.make_the_wall(scan.ranges, center_deg=270, width_deg=30)
        
        elif pattern_name == "empty":
            scan.ranges = [float(RANGE_MAX) for _ in range(NUM_POINTS)]
            
        return scan

def main(args=None):
    rclpy.init(args=args)
    node = MockScanPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()