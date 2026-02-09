# WebDriverAgent 安装指南

WebDriverAgent (WDA) 是 Appium 用来与 iOS 设备通信的中间件，需要被编译并安装到设备上。以下是在 iOS 设备上安装 WebDriverAgent 的详细步骤。

## 前提条件

- macOS 系统
- 已安装 Xcode（最好是最新版本）
- 有效的 Apple 开发者账号（免费账号也可以，但有一些限制）
- iOS 设备已通过 USB 连接到 Mac
- 设备已在 Xcode 中信任（在设备首次连接时会提示）

## 步骤 1: 获取 WebDriverAgent 源代码

有两种方式获取 WebDriverAgent 源代码：

### 方式 1: 通过 Appium 安装的 WebDriverAgent（推荐）

如果你已经安装了 Appium，WebDriverAgent 源代码应该已经包含在 Appium 的安装目录中：

```bash
cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent
```

### 方式 2: 直接从 GitHub 克隆

如果你想使用最新版本的 WebDriverAgent，可以直接从 GitHub 克隆：

```bash
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
```

## 步骤 2: 安装依赖

进入 WebDriverAgent 目录后，运行以下命令安装依赖：

```bash
npm install
```

## 步骤 3: 使用 Xcode 打开 WebDriverAgent 项目

```bash
open WebDriverAgent.xcodeproj
```

## 步骤 4: 配置签名证书

1. 在 Xcode 中，选择左侧导航栏中的 WebDriverAgent 项目
2. 在主窗口中，选择 "Signing & Capabilities" 选项卡
3. 对于每个目标（WebDriverAgentLib 和 WebDriverAgentRunner），执行以下操作：
   - 勾选 "Automatically manage signing"
   - 在 "Team" 下拉菜单中选择你的开发者账号
   - 如果出现任何错误，请点击 "Fix Issue" 按钮

## 步骤 5: 构建并部署 WebDriverAgent

### 方式 1: 使用 Xcode 构建并部署

1. 在 Xcode 中，选择 WebDriverAgentRunner 方案
2. 选择你的 iOS 设备作为目标设备
3. 点击 "Build and Run" 按钮（播放图标）
4. 如果构建成功，WebDriverAgent 应用将安装在你的设备上

### 方式 2: 使用命令行构建并部署

```bash
cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent
xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=YOUR_DEVICE_UDID' test
```

将 `YOUR_DEVICE_UDID` 替换为你的设备 UDID，可以通过以下命令获取：

```bash
xcrun xctrace list devices
```

## 步骤 6: 信任开发者证书

首次在设备上安装 WebDriverAgent 后，需要信任开发者证书：

1. 在 iOS 设备上，打开 "设置" > "通用" > "设备管理" 或 "描述文件与设备管理"
2. 找到你的开发者证书（通常是你的 Apple ID 或开发者账号名称）
3. 点击 "信任"

## 步骤 7: 验证 WebDriverAgent 是否正常工作

WebDriverAgent 安装成功后，可以通过以下方式验证它是否正常工作：

1. 在设备上启动 WebDriverAgent 应用（它会显示一个空白屏幕）
2. 或者，使用以下命令启动 WebDriverAgent 并检查它是否响应：

```bash
cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent
xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=YOUR_DEVICE_UDID' test
```

如果一切正常，你应该能够在终端中看到 WebDriverAgent 的日志输出，包括类似 "ServerURLHere" 的消息。

## 常见问题解决

### 1. 构建失败，出现代码签名错误

- 确保你的开发者账号有效
- 检查设备是否已在 Xcode 中注册
- 尝试在 Xcode 中手动修复签名问题

### 2. 设备上没有显示 WebDriverAgent 应用

- 免费开发者账号的应用有 7 天的有效期，过期后需要重新安装
- 确保你的设备已解锁并信任了开发者证书

### 3. WebDriverAgent 安装成功但 Appium 无法连接

- 检查 Appium 日志中的错误信息
- 确保 Appium 配置中的 `xcodeOrgId` 和 `xcodeSigningId` 设置正确
- 尝试增加 `wdaConnectionTimeout` 值

### 4. 使用免费开发者账号的限制

使用免费 Apple 开发者账号时，有以下限制：

- 应用有 7 天的有效期，之后需要重新安装
- 每个设备上最多可以安装 3 个应用
- 某些功能可能受限

如果你经常使用 Appium 进行 iOS 自动化测试，建议使用付费的 Apple 开发者账号。

## 在 Appium 脚本中使用 WebDriverAgent

安装好 WebDriverAgent 后，确保在 Appium 脚本中正确配置以下选项：

```python
options = XCUITestOptions()
options.xcodeOrgId = "YOUR_TEAM_ID"  # 开发者团队ID
options.xcodeSigningId = "iPhone Developer"
options.useNewWDA = False  # 如果 WebDriverAgent 已经安装，设置为 False
```

这样 Appium 就会使用已安装的 WebDriverAgent，而不是尝试重新安装。
