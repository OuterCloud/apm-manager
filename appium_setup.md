# Appium 设置指南

## 安装 Appium 2.0 及驱动程序

Appium 2.0 与之前的版本有很大不同，驱动程序需要单独安装。以下是设置 Appium 2.0 及其驱动程序的步骤：

### 1. 安装 Appium 2.0

```bash
npm install -g appium@next
```

### 2. 安装 XCUITest 驱动程序（用于 iOS 测试）

```bash
appium driver install xcuitest
```

### 3. 安装 UiAutomator2 驱动程序（用于 Android 测试，如需要）

```bash
appium driver install uiautomator2
```

### 4. 验证安装的驱动程序

```bash
appium driver list --installed
```

应该能看到 xcuitest 和/或 uiautomator2 在已安装的驱动程序列表中。

### 5. 启动 Appium 服务器

```bash
appium
```

## 常见问题

### 1. 找不到驱动程序错误

错误信息：

```
Could not find a driver for automationName 'XCUITest' and platformName 'iOS'
```

解决方案：

- 确保已安装 XCUITest 驱动程序：`appium driver install xcuitest`
- 检查驱动程序是否正确安装：`appium driver list --installed`

如果安装驱动程序时遇到权限问题（EACCES 错误），可以尝试以下解决方案：

#### 方案 1：修复 npm 缓存权限

```bash
# 使用当前用户重新拥有npm缓存目录
sudo chown -R $(whoami) ~/.npm
```

#### 方案 2：使用 npm 配置避开权限问题

```bash
# 设置npm缓存目录到用户可写的位置
npm config set cache ~/.npm-cache --global

# 设置npm前缀到用户可写的位置
npm config set prefix ~/.npm-global

# 将新的bin目录添加到PATH
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

#### 方案 3：使用 npx 安装驱动程序

```bash
npx appium driver install xcuitest
```

#### 方案 4：手动安装驱动程序

```bash
# 创建一个临时目录
mkdir -p ~/appium-drivers && cd ~/appium-drivers

# 克隆XCUITest驱动程序仓库
git clone https://github.com/appium/appium-xcuitest-driver.git
cd appium-xcuitest-driver

# 安装依赖并构建
npm install
npm run build

# 将构建好的驱动程序链接到Appium
cd ~/appium-drivers/appium-xcuitest-driver
npm link

# 在Appium目录中链接驱动程序
cd $(npm root -g)/appium
npm link appium-xcuitest-driver
```

### 2. 连接被拒绝错误

错误信息：

```
HTTPConnectionPool(host='localhost', port=4723): Max retries exceeded with url: /wd/hub/session (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1051dd350>: Failed to establish a new connection: [Errno 61] Connection refused'))
```

解决方案：

- 确保 Appium 服务器正在运行
- 检查 Appium 服务器是否在正确的端口上运行（默认为 4723）
- 在新的终端窗口中运行 `appium` 命令启动服务器

### 3. 路由错误

错误信息：

```
[HTTP] No route found for /wd/hub/session
```

解决方案：

- 在 Appium 2.0 中，URL 路径已更改，不再使用 `/wd/hub` 前缀
- 将连接 URL 从 `http://localhost:4723/wd/hub` 更改为 `http://localhost:4723`

## 其他要求

### iOS 测试要求

- Xcode 和命令行工具
- WebDriverAgent 设置（由 XCUITest 驱动程序自动处理）
- 真机测试需要有效的开发者账户和配置的证书

### Android 测试要求

- Android SDK
- 配置好的 ANDROID_HOME 环境变量
