"""Apm manager"""

from dataclasses import dataclass
import random
from typing import List

from solox.public.apm import AppPerformanceMonitor
from solox.public.common import Devices
from loguru import logger
from ppadb.client import Client as AdbClient
from ppadb.device import Device


@dataclass
class Platform:
    Android = "Android"
    iOS = "iOS"


@dataclass
class AdbConf:
    host = "127.0.0.1"
    port = 5037


class ApmManager:
    def __init__(self, device_id: str, pkg_name: str, platform: str):
        """初始化 Apm Manager"""
        self.adb_client = AdbClient(host=AdbConf.host, port=AdbConf.port)

        self.platform = platform
        self.pkg_name = pkg_name
        self.device_id = device_id or self.get_random_device_id()

        if self.platform == Platform.Android:
            self.check_adb_package_installed()
        elif self.platform == Platform.iOS:
            pass
        else:
            logger.error("平台参数错误")
            raise Exception("平台参数错误")

    def get_adb_devices(self):
        """获取 adb 设备列表"""

        return self.adb_client.devices()

    @staticmethod
    def get_devices():
        """获取 solox 设备列表"""

        return Devices()

    def get_process_list(self, device_id: str, pkg_name: str) -> List[str]:
        """获取进程列表"""

        d = self.get_devices()
        process_list = d.getPid(deviceId=device_id, pkgName=pkg_name)
        return process_list

    def get_random_device_id(self):
        """获取随机设备的 id"""

        device_id = None

        if self.platform == Platform.Android:
            adb_devices = self.get_adb_devices()
            random_adb_device: Device = random.choice(adb_devices)
            device_id = random_adb_device.serial
        elif self.platform == Platform.iOS:
            pass

        if not device_id:
            raise Exception("未找到设备")

        logger.info(f"选取的设备 id 为: {device_id}")
        return device_id

    def check_adb_package_installed(self):
        """检查 adb 设备是否安装包"""

        device: Device = self.adb_client.device(self.device_id)
        logger.info(f"正在检查设备 {self.device_id} 是否安装包 {self.pkg_name}")
        if not device.is_installed(self.pkg_name):
            logger.error(f"设备 {self.device_id} 未安装包 {self.pkg_name}")
            raise Exception(f"设备 {self.device_id} 未安装包 {self.pkg_name}")
        logger.success(f"设备 {self.device_id} 安装了包 {self.pkg_name}")

    def get_pid(self, endswith: str):
        """获取进程名以指定字符串结尾的进程的 pid"""

        pid = None
        process_list: List[str] = self.get_process_list(self.device_id, self.pkg_name)
        for process in process_list:
            if process.endswith(endswith):
                pid = process.split(":")[0]
        if not pid:
            logger.error(f"未找到以 {endswith} 结尾的进程名")
        logger.success(f"找到以 {endswith} 结尾的进程名, pid 为 {pid}")
        return pid

    def collect_all(
        self,
        duration: int,
        report_path: str = None,
        pid: int = None,
        record: bool = False,
    ):
        """采集所有数据"""

        logger.info(
            f"开始采集 {self.platform} 设备 {self.device_id} 包 {self.pkg_name} 下进程 {pid} 的所有性能数据"
        )
        apm = AppPerformanceMonitor(
            pkgName=self.pkg_name,
            platform=self.platform,
            deviceId=self.device_id,
            surfaceview=True,
            noLog=False,
            pid=pid,
            record=record,
            collect_all=True,
            duration=duration,
        )
        apm.collectAll(report_path=report_path)
