#include <chrono>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <csignal>
#include <atomic>

#include <opencv2/calib3d.hpp>
// Includes common necessary includes for development using depthai library
#include "depthai/depthai.hpp"

std::atomic<bool> go_flag(true);

void signalHandler(int signum) {
    go_flag = false;
}

int main(int argc, char** argv) {
    using namespace std::chrono;

    std::signal(SIGINT, signalHandler); // Register handler for Ctrl-C

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
    auto qLeft = device.getOutputQueue("left", 4, false);
    auto qRight = device.getOutputQueue("right", 4, false);
    auto imuQueue = device.getOutputQueue("imu", 200, false);

    std::string home = "oakd_lite/mav0";
    std::filesystem::create_directories(std::filesystem::path(home + "/cam0/data"));
    std::filesystem::create_directories(std::filesystem::path(home + "/cam1/data"));
    std::filesystem::create_directories(std::filesystem::path(home + "/imu0"));
    std::ofstream imu_file(home + "/imu0/data.csv");
    imu_file << std::setprecision(std::numeric_limits<float>::max_digits10);
    std::ofstream cam0_file(home + "/cam0/data.csv");
    cam0_file << std::setprecision(std::numeric_limits<float>::max_digits10);
    std::ofstream cam1_file(home + "/cam1/data.csv");
    cam1_file << std::setprecision(std::numeric_limits<float>::max_digits10);

    while(go_flag) {
        auto q_name = device.getQueueEvent();
        if (q_name == "left") {
            auto frame = qLeft->get<dai::ImgFrame>();
            int64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(frame->getTimestampDevice().time_since_epoch()).count();
            cv::imwrite(home + "/cam0/data/" + std::to_string(ns) + ".png", frame->getCvFrame());
            cam0_file << ns << "," << ns << ".png\n";
        } else if (q_name == "right") {
            auto frame = qRight->get<dai::ImgFrame>();
            int64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(frame->getTimestampDevice().time_since_epoch()).count();
            cv::imwrite(home + "/cam1/data/" + std::to_string(ns) + ".png", frame->getCvFrame());
            cam1_file << ns << "," << ns << ".png\n";
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
                imu_file << ns << "," << gyro_cali(0,0) << "," << -gyro_cali(1,0) << "," << -gyro_cali(2,0) << "," << acc_cali(0,0) << "," << -acc_cali(1,0) << "," << -acc_cali(2,0) << "\n";
            }
        }
    }
    imu_file.close();
    cam0_file.close();
    cam1_file.close();
    std::cout<<"bye\n";
    return 0;
}
