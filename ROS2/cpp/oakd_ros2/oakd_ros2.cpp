#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/header.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "sensor_msgs/msg/image.hpp"

#include <opencv2/calib3d.hpp>

// Includes common necessary includes for development using depthai library
#include "depthai/depthai.hpp"

using namespace std::chrono_literals;

sensor_msgs::msg::Image l_img;
bool l_img_avail = false;
bool img_pub_go = true;

void img_pub_func(rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr l_img_pub) {
    while (img_pub_go) {
        if (l_img_avail) {
            l_img_pub->publish(l_img);
            l_img_avail = false;
        }
        std::this_thread::sleep_for(10ms);
    }
}

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto ros_node = rclcpp::Node::make_shared("oakd");
    auto l_img_pub = ros_node->create_publisher<sensor_msgs::msg::Image>("mono_left", rclcpp::QoS(2).best_effort().durability_volatile());
    auto imu_pub = ros_node->create_publisher<sensor_msgs::msg::Imu>("imu", rclcpp::QoS(20).best_effort().durability_volatile());

    std::thread img_pub_worker(img_pub_func, l_img_pub);

    cv::FileStorage imu_yml;
    imu_yml.open(argv[1], cv::FileStorage::READ);
    cv::Mat acc_mis_align, acc_scale, acc_bias;
    imu_yml["acc_misalign"] >> acc_mis_align;
    imu_yml["acc_scale"] >> acc_scale;
    imu_yml["acc_bias"] >> acc_bias;
    cv::Mat acc_cor = acc_mis_align * acc_scale;
    cv::Mat gyro_mis_align, gyro_scale, gyro_bias;
    imu_yml["gyro_misalign"] >> gyro_mis_align;
    imu_yml["gyro_scale"] >> gyro_scale;
    imu_yml["gyro_bias"] >> gyro_bias;
    cv::Mat gyro_cor = gyro_mis_align * gyro_scale;
    imu_yml.release();

    // Create pipeline
    dai::Pipeline pipeline;

    // Define source and output
    auto monoLeft = pipeline.create<dai::node::MonoCamera>();
    auto xoutLeft = pipeline.create<dai::node::XLinkOut>();
    auto monoRight = pipeline.create<dai::node::MonoCamera>();
    auto xoutRight = pipeline.create<dai::node::XLinkOut>();
    auto imu = pipeline.create<dai::node::IMU>();
    auto xout_imu = pipeline.create<dai::node::XLinkOut>();

    xoutLeft->setStreamName("left");
    xoutRight->setStreamName("right");
    xout_imu->setStreamName("imu");

    // Properties
    monoLeft->setCamera("left");
    monoLeft->setResolution(dai::MonoCameraProperties::SensorResolution::THE_480_P);
    monoLeft->setFps(20);
    monoRight->setCamera("right");
    monoRight->setResolution(dai::MonoCameraProperties::SensorResolution::THE_480_P);
    monoRight->setFps(20);
    imu->enableIMUSensor(dai::IMUSensor::ACCELEROMETER_RAW, 200);
    imu->enableIMUSensor(dai::IMUSensor::GYROSCOPE_RAW, 200);
    imu->setBatchReportThreshold(5);
    imu->setMaxBatchReports(10);

    // Linking
    monoLeft->out.link(xoutLeft->input);
    monoRight->out.link(xoutRight->input);
    imu->out.link(xout_imu->input);

    // Connect to device and start pipeline
    dai::Device device(pipeline);

    std::cout << "Usb speed: " << device.getUsbSpeed() << "\n";
    std::cout << "Device name: " << device.getDeviceName() << " Product name: " << device.getProductName() << "\n";

    // Output queue will be used to get the grayscale frames from the output defined above
    auto qLeft = device.getOutputQueue("left", 2, false);
    auto qRight = device.getOutputQueue("right", 2, false);
    auto imuQueue = device.getOutputQueue("imu", 50, false);

    while(rclcpp::ok()) {
        auto q_name = device.getQueueEvent();
        if (q_name == "left") {
            auto frame = qLeft->get<dai::ImgFrame>();
            int64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(frame->getTimestampDevice().time_since_epoch()).count();
            l_img.header.stamp.sec = static_cast<int32_t>(ns / 1000000000);
            l_img.header.stamp.nanosec = static_cast<uint32_t>(ns % 1000000000);
            l_img.height = frame->getHeight();
            l_img.width = frame->getWidth();
            l_img.is_bigendian = 0;
            l_img.encoding = "mono8";
            l_img.step = l_img.width;
            l_img.data = frame->getData();
            l_img_avail = true;
        } else if (q_name == "right") {
            auto frame = qRight->get<dai::ImgFrame>();
            //int64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(frame->getTimestampDevice().time_since_epoch()).count();
        } else if (q_name == "imu") {
            auto imuData = imuQueue->get<dai::IMUData>();
            auto imuPackets = imuData->packets;
            for(const auto& imuPacket : imuPackets) {
                auto& acc = imuPacket.acceleroMeter;
                auto& gyro = imuPacket.gyroscope;
                cv::Mat acc_raw = (cv::Mat_<double>(3,1) << acc.x, acc.y, acc.z);
                cv::Mat1d acc_cali = acc_cor * (acc_raw - acc_bias);
                cv::Mat gyro_raw = (cv::Mat_<double>(3,1) << gyro.x, gyro.y, gyro.z);
                cv::Mat1d gyro_cali = gyro_cor * (gyro_raw - gyro_bias);
                auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(acc.getTimestampDevice().time_since_epoch()).count();
                sensor_msgs::msg::Imu imu_msg;
                imu_msg.header.frame_id = "body";
                imu_msg.header.stamp.sec = static_cast<int32_t>(ns / 1000000000);
                imu_msg.header.stamp.nanosec = static_cast<uint32_t>(ns % 1000000000);
                imu_msg.linear_acceleration.x = acc_cali(0,0);
                imu_msg.linear_acceleration.y = acc_cali(1,0);
                imu_msg.linear_acceleration.z = acc_cali(2,0);
                imu_msg.angular_velocity.x = gyro_cali(0,0);
                imu_msg.angular_velocity.y = gyro_cali(1,0);
                imu_msg.angular_velocity.z = gyro_cali(2,0);
                imu_pub->publish(imu_msg);
            }
        }
    }
    img_pub_go = false;
    img_pub_worker.join();
    rclcpp::shutdown();
    std::cout<<"bye\n";
    return 0;
}
