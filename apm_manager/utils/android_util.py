import subprocess


def list_android_devices():
    """列出已连接的Android设备"""

    try:
        output = subprocess.check_output(["adb", "devices"], universal_newlines=True)
        print("\n已连接的Android设备:")
        if "device" in output and not "List of devices attached" == output.strip():
            print(output)
            return True
        else:
            print("未检测到Android设备")
            return False
    except Exception as e:
        print(f"获取Android设备列表时出错: {e}")
        return False


def list_android_apps():
    """列出Android设备上已安装的应用"""

    try:
        output = subprocess.check_output(
            ["adb", "shell", "pm", "list", "packages", "-3"], universal_newlines=True
        )
        print("\nAndroid设备上已安装的第三方应用:")
        if output.strip():
            # 格式化输出，去掉"package:"前缀
            apps = [
                line[8:] for line in output.splitlines() if line.startswith("package:")
            ]
            for app in sorted(apps):
                print(f"- {app}")
            return True
        else:
            print("未找到已安装的第三方应用")
            return False
    except Exception as e:
        print(f"获取Android应用列表时出错: {e}")
        return False
