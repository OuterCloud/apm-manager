# 移动应用性能监控工具

这是一个用于监控 iOS 和 Android 应用性能的工具集，可以收集 CPU、内存、电池、网络、FPS 和 GPU 等性能指标，并生成 HTML 格式的性能报告。

## 功能特点

- 支持 iOS 和 Android 平台
- 自动检测和安装必要的依赖
- 监控多种性能指标：CPU、内存、电池、网络、FPS 和 GPU
- 生成可视化 HTML 报告
- 提供报告查看器，方便管理和查看所有报告
- 支持命令行参数和交互式操作模式

## 安装

### 前提条件

- Python 3.6+
- 对于 iOS 设备监控：
  - macOS 系统
  - 已安装 tidevice 工具（脚本会自动安装）
- 对于 Android 设备监控：
  - 已安装 adb 工具（Android 平台工具）

### 安装步骤

1. 克隆或下载此仓库
2. 安装依赖：

```bash
pip install solox tidevice
```

3. 对于 Android 设备监控，安装 adb 工具：

- macOS: `brew install android-platform-tools`
- Windows: 下载并安装 [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
- Linux: `sudo apt-get install android-tools-adb`

## 使用方法

### 基本用法

运行主脚本，将启动交互式界面：

```bash
python monitor_app_performance.py
```

### 命令行参数

```bash
# 列出已连接的设备
python monitor_app_performance.py --list-devices

# 列出设备上已安装的应用
python monitor_app_performance.py --platform ios --list-apps

# 监控特定应用
python monitor_app_performance.py --platform ios --package com.example.app --duration 60

# 启动报告查看器
python monitor_app_performance.py --view-reports
```

### 参数说明

- `--platform`: 选择平台，可选值为 `ios` 或 `android`
- `--device`: 设备 ID（iOS 的 UDID 或 Android 的序列号）
- `--package`: 应用包名（iOS 的 Bundle ID 或 Android 的包名）
- `--duration`: 监控持续时间（秒），默认为 30 秒
- `--list-devices`: 列出已连接的设备
- `--list-apps`: 列出设备上已安装的应用
- `--view-reports`: 启动报告查看器
- `--port`: 报告查看器服务器端口号，默认为 8000

## 报告查看器

报告查看器提供了一个 Web 界面，用于查看和管理所有生成的性能报告。

启动报告查看器：

```bash
python monitor_app_performance.py --view-reports
```

或者直接运行：

```bash
python report_viewer.py
```

报告查看器功能：

- 列出所有生成的性能报告
- 按平台、日期和应用包名筛选报告
- 查看报告详情
- 删除不需要的报告

## 项目结构

- `monitor_app_performance.py`: 主入口脚本
- `monitor_ios_performance.py`: iOS 性能监控脚本
- `monitor_android_performance.py`: Android 性能监控脚本
- `report_viewer.py`: 报告查看器
- `performance_reports/`: 存放生成的性能报告的目录

## 性能指标说明

### CPU

显示应用的 CPU 使用率，包括总体使用率和各个核心的使用情况。

### 内存

显示应用的内存使用情况，包括物理内存和虚拟内存。

### 电池

显示设备的电池使用情况，包括电量和温度。

### 网络

显示应用的网络使用情况，包括上传和下载速度。

### FPS

显示应用的帧率，反映 UI 流畅度。

### GPU

显示应用的 GPU 使用情况。

## 常见问题

### 无法检测到设备

- 确保设备已正确连接到电脑
- 对于 iOS 设备，确保已安装并配置 tidevice
- 对于 Android 设备，确保已启用 USB 调试模式并授权

### 无法监控特定应用

- 确保提供了正确的应用包名
- 对于 iOS 应用，确保应用已安装在设备上
- 对于 Android 应用，确保应用已安装并且可以通过 adb 访问

### 报告生成失败

- 检查是否有足够的磁盘空间
- 确保有权限写入 performance_reports 目录

## 许可证

MIT
