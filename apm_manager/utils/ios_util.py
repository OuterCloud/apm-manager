import subprocess


def list_ios_devices():
    """列出已连接的iOS设备"""

    try:
        output = subprocess.check_output(["tidevice", "list"], universal_newlines=True)
        print("\n已连接的iOS设备:")
        if "UDID" in output:
            print(output)
            return True
        else:
            print("未检测到iOS设备")
            return False
    except Exception as e:
        print(f"获取iOS设备列表时出错: {e}")
        return False


def list_ios_apps(device_id=None):
    """列出iOS设备上已安装的应用"""

    cmd = ["tidevice"]
    if device_id:
        cmd.extend(["-u", device_id])
    cmd.append("applist")

    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        print("\niOS设备上已安装的应用:")
        if output.strip():
            print(output)
            return True
        else:
            print("未找到已安装的应用")
            return False
    except Exception as e:
        print(f"获取iOS应用列表时出错: {e}")
        return False
