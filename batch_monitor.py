#!/usr/bin/env python3
"""
批量应用性能监控工具
支持同时监控多个应用或在不同时间段自动运行测试
"""

import argparse
import json
import sys
import time
from pathlib import Path

import schedule

from monitor_app_performance import (
    list_android_devices,
    list_ios_devices,
    run_android_monitor,
    run_ios_monitor,
)

# 导入主脚本模块
try:
    from monitor_app_performance import (
        check_dependencies,
    )
except ImportError:
    print("错误: 无法导入必要的模块。请确保所有脚本文件在同一目录下。")
    sys.exit(1)

# 配置文件路径
CONFIG_DIR = Path.home() / ".apm_manager"
CONFIG_FILE = CONFIG_DIR / "batch_config.json"

# 默认配置
DEFAULT_CONFIG = {
    "tasks": [
        {
            "name": "iOS示例任务",
            "platform": "ios",
            "package": "com.example.app",
            "duration": 30,
            "enabled": False,
            "schedule": {
                "type": "daily",
                "time": "09:00",
                "days": ["monday", "wednesday", "friday"],
            },
        },
        {
            "name": "Android示例任务",
            "platform": "android",
            "package": "com.example.android",
            "duration": 30,
            "enabled": False,
            "schedule": {"type": "interval", "hours": 2},
        },
    ],
    "report_dir": "performance_reports",
    "notification": {"enabled": False, "email": "", "slack_webhook": ""},
}


def ensure_config():
    """确保配置文件存在，如果不存在则创建默认配置"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"已创建默认配置文件: {CONFIG_FILE}")


def load_config():
    """加载配置文件"""
    ensure_config()
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return DEFAULT_CONFIG


def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"配置已保存到: {CONFIG_FILE}")
    except Exception as e:
        print(f"保存配置文件失败: {e}")


def run_task(task):
    """运行单个监控任务"""
    print(f"\n开始执行任务: {task['name']}")
    print(
        f"平台: {task['platform']}, 应用包名: {task['package']}, 持续时间: {task['duration']}秒"
    )

    # 获取设备列表
    devices = []
    if task["platform"] == "ios":
        devices = list_ios_devices()
    elif task["platform"] == "android":
        devices = list_android_devices()

    if not devices:
        print(f"错误: 未找到{task['platform']}设备")
        return False

    # 使用第一个可用设备
    device_id = devices[0]["id"]
    print(f"使用设备: {device_id}")

    # 运行监控
    try:
        if task["platform"] == "ios":
            run_android_monitor(device_id, task["package"], task["duration"])
        elif task["platform"] == "android":
            run_ios_monitor(device_id, task["package"], task["duration"])

        print(f"任务 {task['name']} 完成")
        return True
    except Exception as e:
        print(f"任务 {task['name']} 执行失败: {e}")
        return False


def run_all_tasks(config):
    """运行所有启用的任务"""
    enabled_tasks = [task for task in config["tasks"] if task.get("enabled", False)]

    if not enabled_tasks:
        print("没有启用的任务")
        return

    print(f"开始执行 {len(enabled_tasks)} 个任务")

    for task in enabled_tasks:
        run_task(task)


def schedule_tasks(config):
    """根据配置调度任务"""
    enabled_tasks = [task for task in config["tasks"] if task.get("enabled", False)]

    if not enabled_tasks:
        print("没有启用的任务")
        return

    print(f"调度 {len(enabled_tasks)} 个任务")

    for task in enabled_tasks:
        if "schedule" in task:
            schedule_info = task["schedule"]

            if schedule_info.get("type") == "daily":
                time_str = schedule_info.get("time", "09:00")
                days = schedule_info.get(
                    "days", ["monday", "tuesday", "wednesday", "thursday", "friday"]
                )

                for day in days:
                    if day.lower() == "monday":
                        schedule.every().monday.at(time_str).do(run_task, task)
                    elif day.lower() == "tuesday":
                        schedule.every().tuesday.at(time_str).do(run_task, task)
                    elif day.lower() == "wednesday":
                        schedule.every().wednesday.at(time_str).do(run_task, task)
                    elif day.lower() == "thursday":
                        schedule.every().thursday.at(time_str).do(run_task, task)
                    elif day.lower() == "friday":
                        schedule.every().friday.at(time_str).do(run_task, task)
                    elif day.lower() == "saturday":
                        schedule.every().saturday.at(time_str).do(run_task, task)
                    elif day.lower() == "sunday":
                        schedule.every().sunday.at(time_str).do(run_task, task)

                print(
                    f"任务 '{task['name']}' 已调度为每周 {', '.join(days)} 的 {time_str} 运行"
                )

            elif schedule_info.get("type") == "interval":
                hours = schedule_info.get("hours", 24)
                schedule.every(hours).hours.do(run_task, task)
                print(f"任务 '{task['name']}' 已调度为每 {hours} 小时运行一次")

    print("\n调度器已启动，按 Ctrl+C 停止")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n调度器已停止")


def list_tasks(config):
    """列出所有任务"""
    print("\n当前配置的任务:")
    print("-" * 80)
    print(
        f"{'ID':<4} {'名称':<20} {'平台':<10} {'包名':<30} {'持续时间':<10} {'状态':<8}"
    )
    print("-" * 80)

    for i, task in enumerate(config["tasks"]):
        status = "启用" if task.get("enabled", False) else "禁用"
        print(
            f"{i:<4} {task['name']:<20} {task['platform']:<10} {task['package']:<30} {task['duration']:<10} {status:<8}"
        )

    print("-" * 80)


def add_task(config):
    """添加新任务"""
    print("\n添加新任务:")

    name = input("任务名称: ")
    platform = input("平台 (ios/android): ").lower()

    while platform not in ["ios", "android"]:
        print("错误: 平台必须是 'ios' 或 'android'")
        platform = input("平台 (ios/android): ").lower()

    package = input("应用包名: ")

    duration = input("监控持续时间(秒) [默认: 30]: ")
    try:
        duration = int(duration) if duration else 30
    except ValueError:
        print("错误: 持续时间必须是整数，使用默认值30")
        duration = 30

    enabled = input("是否启用 (y/n) [默认: y]: ").lower() != "n"

    schedule_type = input("调度类型 (daily/interval/none) [默认: none]: ").lower()
    schedule_info = {}

    if schedule_type == "daily":
        time_str = input("运行时间 (HH:MM) [默认: 09:00]: ") or "09:00"
        days_input = input("运行日 (monday,wednesday,friday) [默认: 所有工作日]: ")

        if days_input:
            days = [day.strip().lower() for day in days_input.split(",")]
        else:
            days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

        schedule_info = {"type": "daily", "time": time_str, "days": days}

    elif schedule_type == "interval":
        hours_input = input("间隔小时数 [默认: 24]: ")
        try:
            hours = int(hours_input) if hours_input else 24
        except ValueError:
            print("错误: 小时数必须是整数，使用默认值24")
            hours = 24

        schedule_info = {"type": "interval", "hours": hours}

    new_task = {
        "name": name,
        "platform": platform,
        "package": package,
        "duration": duration,
        "enabled": enabled,
    }

    if schedule_info:
        new_task["schedule"] = schedule_info

    config["tasks"].append(new_task)
    save_config(config)
    print(f"已添加新任务: {name}")


def edit_task(config):
    """编辑现有任务"""
    list_tasks(config)

    task_id = input("\n输入要编辑的任务ID: ")
    try:
        task_id = int(task_id)
        if task_id < 0 or task_id >= len(config["tasks"]):
            print("错误: 无效的任务ID")
            return
    except ValueError:
        print("错误: 任务ID必须是整数")
        return

    task = config["tasks"][task_id]
    print(f"\n编辑任务: {task['name']}")

    name = input(f"任务名称 [{task['name']}]: ") or task["name"]
    platform = (
        input(f"平台 (ios/android) [{task['platform']}]: ").lower() or task["platform"]
    )

    while platform not in ["ios", "android"]:
        print("错误: 平台必须是 'ios' 或 'android'")
        platform = (
            input(f"平台 (ios/android) [{task['platform']}]: ").lower()
            or task["platform"]
        )

    package = input(f"应用包名 [{task['package']}]: ") or task["package"]

    duration_input = input(f"监控持续时间(秒) [{task['duration']}]: ")
    try:
        duration = int(duration_input) if duration_input else task["duration"]
    except ValueError:
        print(f"错误: 持续时间必须是整数，使用原值 {task['duration']}")
        duration = task["duration"]

    enabled_input = input(
        f"是否启用 (y/n) [{'y' if task.get('enabled', False) else 'n'}]: "
    )
    if enabled_input:
        enabled = enabled_input.lower() == "y"
    else:
        enabled = task.get("enabled", False)

    # 更新任务
    task["name"] = name
    task["platform"] = platform
    task["package"] = package
    task["duration"] = duration
    task["enabled"] = enabled

    # 处理调度信息
    if "schedule" in task:
        edit_schedule = input("编辑调度信息 (y/n) [默认: n]: ").lower() == "y"
        if edit_schedule:
            schedule_type = (
                input(
                    f"调度类型 (daily/interval/none) [{task['schedule']['type']}]: "
                ).lower()
                or task["schedule"]["type"]
            )

            if schedule_type == "none":
                if "schedule" in task:
                    del task["schedule"]
            else:
                schedule_info = {}

                if schedule_type == "daily":
                    current_time = (
                        task["schedule"].get("time", "09:00")
                        if task["schedule"]["type"] == "daily"
                        else "09:00"
                    )
                    time_str = (
                        input(f"运行时间 (HH:MM) [{current_time}]: ") or current_time
                    )

                    current_days = (
                        task["schedule"].get(
                            "days",
                            ["monday", "tuesday", "wednesday", "thursday", "friday"],
                        )
                        if task["schedule"]["type"] == "daily"
                        else ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    )
                    days_input = input(
                        f"运行日 ({','.join(current_days)}) [默认: 不变]: "
                    )

                    if days_input:
                        days = [day.strip().lower() for day in days_input.split(",")]
                    else:
                        days = current_days

                    schedule_info = {"type": "daily", "time": time_str, "days": days}

                elif schedule_type == "interval":
                    current_hours = (
                        task["schedule"].get("hours", 24)
                        if task["schedule"]["type"] == "interval"
                        else 24
                    )
                    hours_input = input(f"间隔小时数 [{current_hours}]: ")
                    try:
                        hours = int(hours_input) if hours_input else current_hours
                    except ValueError:
                        print(f"错误: 小时数必须是整数，使用原值 {current_hours}")
                        hours = current_hours

                    schedule_info = {"type": "interval", "hours": hours}

                task["schedule"] = schedule_info
    else:
        add_schedule = input("添加调度信息 (y/n) [默认: n]: ").lower() == "y"
        if add_schedule:
            schedule_type = (
                input("调度类型 (daily/interval) [默认: daily]: ").lower() or "daily"
            )
            schedule_info = {}

            if schedule_type == "daily":
                time_str = input("运行时间 (HH:MM) [默认: 09:00]: ") or "09:00"
                days_input = input(
                    "运行日 (monday,wednesday,friday) [默认: 所有工作日]: "
                )

                if days_input:
                    days = [day.strip().lower() for day in days_input.split(",")]
                else:
                    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

                schedule_info = {"type": "daily", "time": time_str, "days": days}

            elif schedule_type == "interval":
                hours_input = input("间隔小时数 [默认: 24]: ")
                try:
                    hours = int(hours_input) if hours_input else 24
                except ValueError:
                    print("错误: 小时数必须是整数，使用默认值24")
                    hours = 24

                schedule_info = {"type": "interval", "hours": hours}

            task["schedule"] = schedule_info

    save_config(config)
    print(f"已更新任务: {name}")


def delete_task(config):
    """删除任务"""
    list_tasks(config)

    task_id = input("\n输入要删除的任务ID: ")
    try:
        task_id = int(task_id)
        if task_id < 0 or task_id >= len(config["tasks"]):
            print("错误: 无效的任务ID")
            return
    except ValueError:
        print("错误: 任务ID必须是整数")
        return

    task = config["tasks"][task_id]
    confirm = input(f"确定要删除任务 '{task['name']}' 吗? (y/n): ").lower() == "y"

    if confirm:
        del config["tasks"][task_id]
        save_config(config)
        print(f"已删除任务: {task['name']}")
    else:
        print("取消删除")


def interactive_menu():
    """交互式菜单"""
    config = load_config()

    while True:
        print("\n批量应用性能监控工具")
        print("=" * 50)
        print("1. 列出所有任务")
        print("2. 添加新任务")
        print("3. 编辑任务")
        print("4. 删除任务")
        print("5. 运行所有启用的任务")
        print("6. 启动调度器")
        print("0. 退出")
        print("=" * 50)

        choice = input("请选择操作: ")

        if choice == "1":
            list_tasks(config)
        elif choice == "2":
            add_task(config)
        elif choice == "3":
            edit_task(config)
        elif choice == "4":
            delete_task(config)
        elif choice == "5":
            run_all_tasks(config)
        elif choice == "6":
            schedule_tasks(config)
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("无效的选择，请重试")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量应用性能监控工具")
    parser.add_argument("--run", action="store_true", help="运行所有启用的任务")
    parser.add_argument("--schedule", action="store_true", help="启动调度器")
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--add", action="store_true", help="添加新任务")
    parser.add_argument("--edit", type=int, help="编辑指定ID的任务")
    parser.add_argument("--delete", type=int, help="删除指定ID的任务")

    args = parser.parse_args()
    config = load_config()

    # 检查依赖
    check_dependencies()

    if args.list:
        list_tasks(config)
    elif args.add:
        add_task(config)
    elif args.edit is not None:
        if args.edit < 0 or args.edit >= len(config["tasks"]):
            print(f"错误: 无效的任务ID {args.edit}")
        else:
            task = config["tasks"][args.edit]
            print(f"\n编辑任务: {task['name']}")
            # 简化版的编辑功能
            enabled = input(
                f"是否启用 (y/n) [{'y' if task.get('enabled', False) else 'n'}]: "
            )
            if enabled:
                task["enabled"] = enabled.lower() == "y"
                save_config(config)
                print(f"已更新任务: {task['name']}")
    elif args.delete is not None:
        if args.delete < 0 or args.delete >= len(config["tasks"]):
            print(f"错误: 无效的任务ID {args.delete}")
        else:
            task = config["tasks"][args.delete]
            confirm = (
                input(f"确定要删除任务 '{task['name']}' 吗? (y/n): ").lower() == "y"
            )
            if confirm:
                del config["tasks"][args.delete]
                save_config(config)
                print(f"已删除任务: {task['name']}")
    elif args.run:
        run_all_tasks(config)
    elif args.schedule:
        schedule_tasks(config)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
