# 常见问题排查指南

## tidevice 模块错误: No module named 'pkg_resources'

### 问题描述

当运行 tidevice 相关命令时，出现以下错误：

```
Traceback (most recent call last):
  File "/Users/hanqi01/solox/bin/tidevice", line 5, in <module>
    from tidevice.__main__ import main
  File "/Users/hanqi01/solox/lib/python3.12/site-packages/tidevice/__main__.py", line 36, in <module>
    from ._version import __version__
  File "/Users/hanqi01/solox/lib/python3.12/site-packages/tidevice/_version.py", line 4, in <module>
    import pkg_resources
ModuleNotFoundError: No module named 'pkg_resources'
```

### 原因

这个错误是因为缺少`pkg_resources`模块，该模块是`setuptools`包的一部分。在 Python 3.12 中，`pkg_resources`不再是`setuptools`的默认安装部分，需要单独安装或确保安装了完整的`setuptools`。

### 解决方案

1. 重新安装 setuptools：

```bash
pip install --upgrade setuptools
```

2. 确保 tidevice 安装正确：

```bash
pip uninstall tidevice
pip install tidevice==0.12.10
```

3. 如果使用虚拟环境，请确保在虚拟环境中安装这些包：

```bash
# 激活虚拟环境
source /Users/hanqi01/solox/bin/activate

# 安装依赖
pip install --upgrade setuptools
pip install tidevice==0.12.10
```

4. 如果上述方法不起作用，可以尝试重新创建虚拟环境：

```bash
# 创建新的虚拟环境
python -m venv /Users/hanqi01/solox_new

# 激活新环境
source /Users/hanqi01/solox_new/bin/activate

# 安装所有依赖
pip install -r requirements.txt
```

### 预防措施

我们已经更新了`requirements.txt`文件，明确添加了 setuptools 作为依赖项。在未来的安装中，只需确保使用最新的 requirements.txt 文件进行安装：

```bash
pip install -r requirements.txt
```

这将安装所有必要的依赖，包括解决此问题所需的 setuptools。

## Appium 连接问题

### 问题描述

在使用 Appium 进行性能监控时，可能会遇到以下几种常见错误：

#### 1. 连接被拒绝错误

```
HTTPConnectionPool(host='localhost', port=4723): Max retries exceeded with url: /wd/hub/session (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1051dd350>: Failed to establish a new connection: [Errno 61] Connection refused'))
```

#### 2. 路由错误

```
[HTTP] No route found for /wd/hub/session
```

#### 3. 驱动程序错误

```
Could not find a driver for automationName 'XCUITest' and platformName 'iOS'
```

### 原因

1. Appium 服务器未运行或端口不正确
2. Appium 2.0 版本的路由路径已更改
3. 缺少必要的驱动程序（如 XCUITest 驱动程序）

### 解决方案

#### 1. 确保 Appium 服务器正在运行

在新的终端窗口中运行：

```bash
appium
```

#### 2. 修正连接 URL

在 Appium 2.0 中，URL 路径已更改，不再使用 `/wd/hub` 前缀：

```python
# 旧版本（Appium 1.x）
driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)

# 新版本（Appium 2.0+）
driver = webdriver.Remote("http://localhost:4723", options=options)
```

#### 3. 安装必要的驱动程序

对于 iOS 测试，需要安装 XCUITest 驱动程序：

```bash
appium driver install xcuitest
```

如果遇到权限问题，可以尝试：

```bash
sudo chown -R $(whoami) ~/.npm
```

#### 4. 检查驱动程序是否正确安装

```bash
appium driver list --installed
```

### 预防措施

我们已经更新了 `appium_perf_monitor.py` 脚本，添加了自动检查 Appium 服务器和驱动程序状态的功能。此外，我们还创建了 `appium_setup.md` 文件，提供了详细的 Appium 设置指南。

在运行性能监控脚本之前，请确保：

1. Appium 服务器正在运行
2. 已安装必要的驱动程序
3. 使用正确的连接 URL

详细设置指南请参考 `appium_setup.md` 文件。
