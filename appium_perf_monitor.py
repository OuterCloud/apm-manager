# pip install Appium-Python-Client
# pkill -f appium
# appium --use-drivers xcuitest


import base64
import os
import re
import subprocess
import sys

import requests
from appium import webdriver
from appium.options.ios import XCUITestOptions


def check_appium_server():
    """检查Appium服务器是否正在运行"""
    try:
        response = requests.get("http://localhost:4723/status", timeout=5)
        if response.status_code == 200:
            print("✅ Appium服务器正在运行")
            return True
        else:
            print(f"❌ Appium服务器返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Appium服务器，请确保Appium已启动")
        print("   运行命令: appium")
        return False
    except Exception as e:
        print(f"❌ 检查Appium服务器时出错: {e}")
        return False


def check_appium_drivers():
    """检查是否安装了必要的Appium驱动程序"""
    try:
        # 使用 subprocess.Popen 来运行命令
        process = subprocess.Popen(
            ["appium", "driver", "list", "--installed"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=dict(os.environ),  # 使用当前的环境变量
        )

        stdout, stderr = process.communicate()

        print("\n=== Appium驱动程序列表 ===")
        print("标准输出:")
        print(stdout)
        print("\n标准错误:")
        print(stderr)
        print("==========================\n")

        # 检查命令是否成功执行
        if process.returncode != 0:
            print("❌ 执行 appium driver list 命令失败")
            print(f"错误输出: {stderr}")
            return False

        # 检查是否包含 xcuitest（同时检查 stdout 和 stderr）
        combined_output = stdout + stderr
        if "xcuitest" in combined_output.lower():
            # 提取版本信息
            version_match = re.search(r"xcuitest@(\d+\.\d+\.\d+)", combined_output)
            version = version_match.group(1) if version_match else "未知版本"

            print(f"✅ XCUITest驱动程序已安装 (版本: {version})")
            return True

        # 如果上述方法失败，尝试直接检查 npm 全局安装目录
        try:
            npm_prefix = subprocess.check_output(
                ["npm", "config", "get", "prefix"], text=True
            ).strip()
            driver_path = os.path.join(
                npm_prefix, "lib", "node_modules", "appium-xcuitest-driver"
            )

            if os.path.exists(driver_path):
                print(f"✅ 在 {driver_path} 找到XCUITest驱动程序")
                return True
        except Exception as npm_error:
            print(f"检查 npm 目录失败: {npm_error}")

        print("❌ 未找到XCUITest驱动程序")
        print("   请运行: appium driver install xcuitest")
        print("   如果遇到权限问题，请参考appium_setup.md文件")
        return False

    except Exception as e:
        print(f"❌ 检查Appium驱动程序时出错: {e}")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   详细信息: {str(e)}")
        return False


def check_xcuitest_driver_path():
    """检查XCUITest驱动程序的安装路径"""
    try:
        # 检查全局安装的驱动程序
        result = subprocess.run(
            ["npm", "list", "-g", "appium-xcuitest-driver"],
            capture_output=True,
            text=True,
        )
        print("\n=== 全局安装的XCUITest驱动程序 ===")
        print(result.stdout)

        # 检查本地安装的驱动程序
        result = subprocess.run(
            ["npm", "list", "appium-xcuitest-driver"], capture_output=True, text=True
        )
        print("\n=== 本地安装的XCUITest驱动程序 ===")
        print(result.stdout)

        # 检查Appium插件目录
        home_dir = subprocess.run(
            ["echo", "$HOME"], capture_output=True, text=True
        ).stdout.strip()
        appium_dir = f"{home_dir}/.appium"

        result = subprocess.run(
            ["ls", "-la", appium_dir], capture_output=True, text=True
        )
        print("\n=== Appium目录内容 ===")
        print(result.stdout)

        return True
    except Exception as e:
        print(f"❌ 检查XCUITest驱动程序路径时出错: {e}")
        return False


# 检查Appium服务器和驱动程序
if not check_appium_server():
    print("\n请先启动Appium服务器，然后再运行此脚本")
    print("详细说明请参考appium_setup.md文件")
    sys.exit(1)

# 检查驱动程序
drivers_ok = check_appium_drivers()
check_xcuitest_driver_path()  # 无论驱动程序检查结果如何，都执行路径检查以获取更多信息

if not drivers_ok:
    print("\n请先安装必要的驱动程序，然后再运行此脚本")
    print("详细说明请参考appium_setup.md文件")
    sys.exit(1)

# 设置 Appium Options
options = XCUITestOptions()
options.platform_name = "iOS"
options.platform_version = "17.7"  # 真机的iOS版本
options.device_name = "zenkilan"  # 真机的名称
options.udid = "00008120-00114D801E40201E"  # 真机的UDID
options.bundle_id = "com.example.app"
options.automation_name = "XCUITest"

# 添加WebDriverAgent相关配置
options.use_new_wda = False  # 使用已安装的WebDriverAgent实例
options.show_xcode_log = True  # 显示Xcode日志以便调试
options.update_wda_bundleid = None  # 使用自定义的WDA Bundle ID，如果需要
options.prevent_wda_attachments = True  # 防止WDA创建不必要的附件
options.simple_isvisible_check = True  # 使用简单的可见性检查以提高性能

# 添加开发者签名相关配置
# 通过 security find-identity -v -p codesigning 命令获取的签名身份
options.xcodeOrgId = "35JC7RPPDN"  # 开发者团队ID
options.xcodeSigningId = "iPhone Developer"

# 添加其他可能有用的配置
options.connect_hardware_keyboard = False
options.wda_local_port = 8100  # 指定WDA使用的端口
options.wda_connection_timeout = 180000  # 增加WDA连接超时时间（毫秒）

print("正在连接到Appium服务器...")
try:
    # 启动 Appium WebDriver
    driver = webdriver.Remote(
        "http://localhost:4723", options=options
    )  # 新版Appium不再需要/wd/hub
    print("✅ 成功连接到Appium服务器")
except Exception as e:
    print(f"❌ 连接到Appium服务器时出错: {e}")
    print("详细说明请参考appium_setup.md文件")
    sys.exit(1)

# 启动性能记录
args = {
    "pid": "current",
    "profileName": "Time Profiler",
    "timeout": 60000,  # 设置超时时间为 60 秒
}
driver.execute_script("mobile: startPerfRecord", args)

# 执行需要分析的操作
# driver.find_element_by_id('some_element').click()

# 停止性能记录并获取数据
args = {"profileName": "Time Profiler"}
b64_zip = driver.execute_script("mobile: stopPerfRecord", args)

# 将 base64 编码的 zip 文件保存到本地
with open("perf_data.zip", "wb") as f:
    f.write(base64.b64decode(b64_zip))

# 关闭 WebDriver
driver.quit()
