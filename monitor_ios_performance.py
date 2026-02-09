#!/usr/bin/env python3
"""
iOS应用性能监控脚本
使用solox库的AppPerformanceMonitor来监控iOS应用的性能指标
"""

import os
import time

from solox.public.apm import AppPerformanceMonitor, Platform

# 设置参数
DEVICE_ID = "00008101-000275623AC1001E"  # 你的iOS设备UDID
PKG_NAME = "com.example.app"  # 要监控的应用Bundle ID
# 你可以替换为你想监控的应用


def monitor_specific_metrics():
    """监控特定的性能指标"""
    print(f"开始监控应用 {PKG_NAME} 的性能...")

    # 创建AppPerformanceMonitor实例
    # pid参数是可选的，如果不提供，AppPerformanceMonitor会尝试自动获取
    monitor = AppPerformanceMonitor(
        pkgName=PKG_NAME,
        platform=Platform.iOS,
        deviceId=DEVICE_ID,
        noLog=False,  # 设置为False以记录日志
        collect_all=False,  # 不自动收集所有性能数据
    )

    # 收集CPU使用率
    print("收集CPU使用率...")
    cpu_info = monitor.collectCpu()
    print(f"CPU信息: {cpu_info}")

    # 收集内存使用情况
    print("收集内存使用情况...")
    memory_info = monitor.collectMemory()
    print(f"内存信息: {memory_info}")

    # 收集电池信息
    print("收集电池信息...")
    battery_info = monitor.collectBattery()
    print(f"电池信息: {battery_info}")

    # 收集网络流量
    print("收集网络流量...")
    network_info = monitor.collectNetwork()
    print(f"网络信息: {network_info}")

    # 收集FPS
    print("收集FPS...")
    fps_info = monitor.collectFps()
    print(f"FPS信息: {fps_info}")

    # 收集GPU使用率
    print("收集GPU使用率...")
    gpu_info = monitor.collectGpu()
    print(f"GPU信息: {gpu_info}")


def monitor_all_metrics(duration=60):
    """收集所有性能指标并生成报告"""
    print(f"开始监控应用 {PKG_NAME} 的所有性能指标，持续 {duration} 秒...")

    # 创建AppPerformanceMonitor实例
    monitor = AppPerformanceMonitor(
        pkgName=PKG_NAME,
        platform=Platform.iOS,
        deviceId=DEVICE_ID,
        noLog=False,  # 设置为False以记录日志
        collect_all=True,  # 收集所有性能数据
        duration=duration,  # 监控持续时间(秒)，设置为0表示一直运行直到手动停止
    )

    # 收集所有性能指标并生成HTML报告
    # 使用时间戳创建唯一的报告文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(os.getcwd(), "performance_reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"performance_report_{timestamp}.html")

    print(f"生成性能报告到: {report_path}")
    monitor.collectAll(report_path=report_path)


if __name__ == "__main__":
    # 选择要运行的监控模式
    # 1. 监控特定指标
    # monitor_specific_metrics()

    # 2. 监控所有指标并生成报告（持续5秒）
    monitor_all_metrics(duration=5)
