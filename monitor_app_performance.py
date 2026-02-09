#!/usr/bin/env python3
"""
应用性能监控主脚本
提供命令行界面，用于选择监控iOS或Android设备上的应用性能
"""

import importlib.util
import sys
import argparse
import subprocess

from apm_manager.utils.android_util import list_android_apps, list_android_devices
from apm_manager.utils.ios_util import list_ios_apps, list_ios_devices


def check_dependencies():
    """检查必要的依赖是否已安装"""

    try:
        if importlib.util.find_spec("solox") is not None:
            print("✓ solox库已安装")
    except ImportError:
        print("✗ solox库未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "solox"])
        print("✓ solox库安装完成")

    # 检查iOS设备连接工具
    try:
        subprocess.check_output(["tidevice", "--version"], stderr=subprocess.STDOUT)
        print("✓ tidevice工具已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ tidevice工具未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tidevice"])
        print("✓ tidevice工具安装完成")

    # 检查Android设备连接工具
    try:
        subprocess.check_output(["adb", "version"], stderr=subprocess.STDOUT)
        print("✓ adb工具已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ adb工具未安装")
        if sys.platform == "darwin":  # macOS
            print("请通过以下命令安装Android平台工具:")
            print("  brew install android-platform-tools")
        elif sys.platform == "win32":  # Windows
            print("请下载并安装Android SDK平台工具:")
            print("  https://developer.android.com/studio/releases/platform-tools")
        elif sys.platform.startswith("linux"):  # Linux
            print("请通过包管理器安装Android平台工具:")
            print("  sudo apt-get install android-tools-adb")
        print("安装后请重新运行此脚本")


def run_ios_monitor(device_id, package_name, duration):
    """运行iOS性能监控"""

    from monitor_ios_performance import monitor_all_metrics

    # 更新设备ID和包名
    import monitor_ios_performance

    monitor_ios_performance.DEVICE_ID = device_id
    monitor_ios_performance.PKG_NAME = package_name

    # 运行监控
    monitor_all_metrics(duration=duration)


def run_android_monitor(device_id, package_name, duration):
    """运行Android性能监控"""

    from monitor_android_performance import monitor_all_metrics

    # 更新设备ID和包名
    import monitor_android_performance

    monitor_android_performance.DEVICE_ID = device_id
    monitor_android_performance.PKG_NAME = package_name

    # 运行监控
    monitor_all_metrics(duration=duration)


def run_report_viewer(port=8000):
    """启动报告查看器"""

    try:
        from report_viewer import start_server

        start_server(port)
    except ImportError as e:
        print(f"启动报告查看器失败: {e}")
        print("请确保report_viewer.py文件存在于当前目录")


def main():
    """主函数"""

    parser = argparse.ArgumentParser(description="应用性能监控工具")
    parser.add_argument(
        "--platform", choices=["ios", "android"], help="选择平台: ios 或 android"
    )
    parser.add_argument("--device", help="设备ID (iOS的UDID或Android的序列号)")
    parser.add_argument("--package", help="应用包名 (iOS的Bundle ID或Android的包名)")
    parser.add_argument(
        "--duration", type=int, default=30, help="监控持续时间(秒)，默认30秒"
    )
    parser.add_argument("--list-devices", action="store_true", help="列出已连接的设备")
    parser.add_argument(
        "--list-apps", action="store_true", help="列出设备上已安装的应用"
    )
    parser.add_argument("--view-reports", action="store_true", help="启动报告查看器")
    parser.add_argument("--port", type=int, default=8000, help="报告查看器服务器端口号")

    args = parser.parse_args()

    # 启动报告查看器
    if args.view_reports:
        print(f"启动报告查看器，端口: {args.port}")
        run_report_viewer(args.port)
        return

    # 检查依赖
    check_dependencies()

    # 列出设备
    if args.list_devices:
        ios_devices = list_ios_devices()
        android_devices = list_android_devices()
        if not ios_devices and not android_devices:
            print("\n未检测到任何设备，请确保设备已正确连接")
        return

    # 列出应用
    if args.list_apps:
        if args.platform == "ios":
            list_ios_apps(args.device)
        elif args.platform == "android":
            list_android_apps()
        else:
            ios_devices = list_ios_devices()
            if ios_devices:
                list_ios_apps(args.device)

            android_devices = list_android_devices()
            if android_devices:
                list_android_apps()
        return

    # 运行监控
    if args.platform and args.package:
        print(
            f"\n开始监控 {args.platform} 平台上的 {args.package} 应用，持续 {args.duration} 秒..."
        )

        if args.platform == "ios":
            run_ios_monitor(args.device, args.package, args.duration)
        else:  # android
            run_android_monitor(args.device, args.package, args.duration)
    else:
        # 交互式选择
        print("\n请选择要监控的平台:")
        print("1. iOS")
        print("2. Android")
        choice = input("请输入选项 (1/2): ")

        if choice == "1":
            # iOS监控
            list_ios_devices()
            device_id = input("\n请输入iOS设备UDID (直接回车使用默认设备): ")
            list_ios_apps(device_id)
            package_name = input("\n请输入要监控的应用Bundle ID: ")
            duration = input("\n请输入监控持续时间(秒) (直接回车使用默认值30秒): ")
            duration = int(duration) if duration.isdigit() else 30

            run_ios_monitor(device_id, package_name, duration)
        elif choice == "2":
            # Android监控
            list_android_devices()
            device_id = input("\n请输入Android设备ID (直接回车使用默认设备): ")
            list_android_apps()
            package_name = input("\n请输入要监控的应用包名: ")
            duration = input("\n请输入监控持续时间(秒) (直接回车使用默认值30秒): ")
            duration = int(duration) if duration.isdigit() else 30

            run_android_monitor(device_id, package_name, duration)
        else:
            print("无效的选项")


if __name__ == "__main__":
    main()
