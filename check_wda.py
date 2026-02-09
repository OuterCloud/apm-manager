#!/usr/bin/env python3
"""
WebDriverAgent 检查工具

此脚本用于检查 WebDriverAgent 的安装状态，并提供帮助信息。
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def print_header(title):
    """打印带格式的标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def run_command(command, shell=False):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1


def check_xcode_installation():
    """检查 Xcode 是否已安装"""
    print_header("检查 Xcode 安装")

    stdout, stderr, returncode = run_command(["xcode-select", "--print-path"])

    if returncode == 0:
        xcode_path = stdout.strip()
        print(f"✅ Xcode 已安装: {xcode_path}")

        # 检查 Xcode 版本
        stdout, stderr, returncode = run_command(["xcodebuild", "-version"])
        if returncode == 0:
            print(f"Xcode 版本信息:\n{stdout}")
        else:
            print(f"⚠️ 无法获取 Xcode 版本: {stderr}")

        return True
    else:
        print("❌ Xcode 未安装或路径无法访问")
        print("请安装 Xcode 并运行 'xcode-select --install'")
        return False


def check_ios_devices():
    """检查连接的 iOS 设备"""
    print_header("检查连接的 iOS 设备")

    stdout, stderr, returncode = run_command(["xcrun", "xctrace", "list", "devices"])

    if returncode == 0 and stdout:
        print("已连接的设备:")
        print(stdout)

        # 检查是否有真实设备连接
        lines = stdout.strip().split("\n")
        devices = [
            line
            for line in lines
            if "(" in line and ")" in line and not "Simulator" in line
        ]

        if devices:
            print(f"✅ 检测到 {len(devices)} 个真实 iOS 设备")
            return True
        else:
            print("⚠️ 未检测到真实 iOS 设备，只有模拟器")
            return False
    else:
        print(f"❌ 无法列出 iOS 设备: {stderr}")
        return False


def check_developer_account():
    """检查开发者账号"""
    print_header("检查开发者账号")

    stdout, stderr, returncode = run_command(
        ["security", "find-identity", "-v", "-p", "codesigning"]
    )

    if returncode == 0 and "valid identities found" in stdout:
        print("可用的签名身份:")
        print(stdout)

        # 提取团队 ID
        import re

        team_id_match = re.search(r"\(([A-Z0-9]+)\)", stdout)
        if team_id_match:
            team_id = team_id_match.group(1)
            print(f"✅ 找到开发者团队 ID: {team_id}")
            print(f"   在 Appium 脚本中使用此 ID 作为 xcodeOrgId")
        else:
            print("⚠️ 无法从签名身份中提取团队 ID")

        return True
    else:
        print("❌ 未找到有效的签名身份")
        print("请确保你已登录 Apple 开发者账号:")
        print("1. 打开 Xcode")
        print("2. 转到 Preferences > Accounts")
        print("3. 添加你的 Apple ID")
        print("4. 下载签名证书")
        return False


def check_wda_source():
    """检查 WebDriverAgent 源代码"""
    print_header("检查 WebDriverAgent 源代码")

    # 检查 Appium 安装的 WebDriverAgent
    home_dir = str(Path.home())
    appium_wda_path = os.path.join(
        home_dir,
        ".appium",
        "node_modules",
        "appium-xcuitest-driver",
        "node_modules",
        "appium-webdriveragent",
    )

    if os.path.exists(appium_wda_path):
        print(f"✅ 在 Appium 安装目录中找到 WebDriverAgent: {appium_wda_path}")

        # 检查 WebDriverAgent.xcodeproj
        wda_project = os.path.join(appium_wda_path, "WebDriverAgent.xcodeproj")
        if os.path.exists(wda_project):
            print(f"✅ 找到 WebDriverAgent Xcode 项目: {wda_project}")
        else:
            print(f"❌ 未找到 WebDriverAgent Xcode 项目")

        return appium_wda_path
    else:
        print(f"❌ 在 Appium 安装目录中未找到 WebDriverAgent")
        print("请确保已安装 Appium 和 XCUITest 驱动程序:")
        print("npm install -g appium")
        print("appium driver install xcuitest")

        # 检查是否有手动克隆的 WebDriverAgent
        wda_paths = [
            os.path.join(home_dir, "WebDriverAgent"),
            os.path.join(os.getcwd(), "WebDriverAgent"),
        ]

        for path in wda_paths:
            if os.path.exists(path) and os.path.exists(
                os.path.join(path, "WebDriverAgent.xcodeproj")
            ):
                print(f"✅ 找到手动克隆的 WebDriverAgent: {path}")
                return path

        print("如果你想手动克隆 WebDriverAgent:")
        print("git clone https://github.com/appium/WebDriverAgent.git")
        print("cd WebDriverAgent")
        print("npm install")

        return None


def check_wda_installation(device_udid=None):
    """检查设备上是否安装了 WebDriverAgent"""
    print_header("检查设备上的 WebDriverAgent 安装")

    if not device_udid:
        # 尝试获取连接的设备 UDID
        stdout, stderr, returncode = run_command(
            ["xcrun", "xctrace", "list", "devices"]
        )

        if returncode == 0 and stdout:
            import re

            # 查找第一个非模拟器设备
            device_match = re.search(r"([^\(]+)\s+\(([0-9A-F\-]+)\)", stdout)
            if device_match and "Simulator" not in device_match.group(1):
                device_name = device_match.group(1).strip()
                device_udid = device_match.group(2).strip()
                print(f"找到设备: {device_name} (UDID: {device_udid})")
            else:
                print("❌ 未找到连接的 iOS 设备")
                return False
        else:
            print(f"❌ 无法列出 iOS 设备: {stderr}")
            return False

    # 检查设备上安装的应用
    stdout, stderr, returncode = run_command(
        ["ideviceinstaller", "-u", device_udid, "-l"]
    )

    if returncode == 0:
        if "com.facebook.WebDriverAgentRunner" in stdout:
            print("✅ WebDriverAgent 已安装在设备上")
            return True
        else:
            print("❌ WebDriverAgent 未安装在设备上")

            # 检查是否安装了 ideviceinstaller
            if "command not found" in stderr:
                print("⚠️ 未安装 ideviceinstaller 工具")
                print("请安装 ideviceinstaller:")
                print("brew install ideviceinstaller")

            return False
    else:
        print(f"❌ 无法检查设备上的应用: {stderr}")

        # 如果 ideviceinstaller 命令不存在
        if "command not found" in stderr:
            print("请安装 ideviceinstaller:")
            print("brew install ideviceinstaller")

        return False


def try_build_wda(wda_path, device_udid=None):
    """尝试构建并部署 WebDriverAgent"""
    print_header("尝试构建并部署 WebDriverAgent")

    if not wda_path or not os.path.exists(wda_path):
        print("❌ WebDriverAgent 路径无效")
        return False

    if not device_udid:
        # 尝试获取连接的设备 UDID
        stdout, stderr, returncode = run_command(
            ["xcrun", "xctrace", "list", "devices"]
        )

        if returncode == 0 and stdout:
            import re

            # 查找第一个非模拟器设备
            device_match = re.search(r"([^\(]+)\s+\(([0-9A-F\-]+)\)", stdout)
            if device_match and "Simulator" not in device_match.group(1):
                device_name = device_match.group(1).strip()
                device_udid = device_match.group(2).strip()
                print(f"找到设备: {device_name} (UDID: {device_udid})")
            else:
                print("❌ 未找到连接的 iOS 设备")
                return False
        else:
            print(f"❌ 无法列出 iOS 设备: {stderr}")
            return False

    # 切换到 WebDriverAgent 目录
    os.chdir(wda_path)

    print("正在构建 WebDriverAgent...")
    print("这可能需要几分钟时间，请耐心等待...")

    # 构建 WebDriverAgent
    build_cmd = [
        "xcodebuild",
        "-project",
        "WebDriverAgent.xcodeproj",
        "-scheme",
        "WebDriverAgentRunner",
        "-destination",
        f"id={device_udid}",
        "test",
    ]

    # 使用 Popen 启动进程，这样我们可以实时获取输出
    process = subprocess.Popen(
        build_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # 设置超时时间（秒）
    timeout = 60
    start_time = time.time()
    wda_url = None

    try:
        # 读取输出并检查 WDA 是否启动
        for line in iter(process.stdout.readline, ""):
            # 打印输出
            print(line, end="")

            # 检查是否包含 WDA 服务器 URL
            if "ServerURLHere" in line:
                wda_url_match = re.search(r"ServerURLHere->(.*)<-ServerURLHere", line)
                if wda_url_match:
                    wda_url = wda_url_match.group(1).strip()
                    print(f"\n✅ WebDriverAgent 已成功启动: {wda_url}")
                    break

            # 检查是否超时
            if time.time() - start_time > timeout:
                print("\n⚠️ 等待 WebDriverAgent 启动超时")
                break
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了构建过程")
    finally:
        # 终止进程
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    if wda_url:
        print("\n✅ WebDriverAgent 构建和部署成功")
        print("现在你可以在 Appium 脚本中使用以下配置:")
        print("options.use_new_wda = False")
        print('options.xcodeOrgId = "YOUR_TEAM_ID"  # 替换为你的团队 ID')
        print('options.xcodeSigningId = "iPhone Developer"')
        return True
    else:
        print("\n❌ WebDriverAgent 构建或部署失败")
        print("请检查上面的错误信息，并参考 webdriveragent_setup.md 文件")
        return False


def main():
    """主函数"""
    print_header("WebDriverAgent 检查工具")
    print("此工具将帮助你检查 WebDriverAgent 的安装状态，并提供帮助信息。")

    # 检查 Xcode
    xcode_ok = check_xcode_installation()
    if not xcode_ok:
        print("\n请先安装 Xcode，然后再运行此脚本")
        sys.exit(1)

    # 检查 iOS 设备
    devices_ok = check_ios_devices()
    if not devices_ok:
        print("\n请连接 iOS 设备，然后再运行此脚本")
        sys.exit(1)

    # 检查开发者账号
    dev_account_ok = check_developer_account()
    if not dev_account_ok:
        print("\n请先配置开发者账号，然后再运行此脚本")
        sys.exit(1)

    # 检查 WebDriverAgent 源代码
    wda_path = check_wda_source()
    if not wda_path:
        print("\n请先安装 Appium 和 XCUITest 驱动程序，或手动克隆 WebDriverAgent 仓库")
        sys.exit(1)

    # 检查设备上是否安装了 WebDriverAgent
    wda_installed = check_wda_installation()

    # 如果 WebDriverAgent 未安装，询问用户是否要尝试安装
    if not wda_installed:
        print("\n是否要尝试构建并部署 WebDriverAgent？")
        print("1. 是")
        print("2. 否")
        choice = input("请选择 (1/2): ")

        if choice == "1":
            try_build_wda(wda_path)
        else:
            print("\n请参考 webdriveragent_setup.md 文件，手动安装 WebDriverAgent")
    else:
        print("\nWebDriverAgent 已安装在设备上。")
        print("你可以在 Appium 脚本中使用以下配置:")
        print("options.use_new_wda = False")
        print('options.xcodeOrgId = "YOUR_TEAM_ID"  # 替换为你的团队 ID')
        print('options.xcodeSigningId = "iPhone Developer"')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断了脚本执行")
        sys.exit(0)
