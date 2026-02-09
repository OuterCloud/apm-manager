#!/bin/bash

# 安装 iOS 开发和测试所需的依赖项
echo "===== 安装 iOS 开发和测试所需的依赖项 ====="

# 检查 Homebrew 是否已安装
if ! command -v brew &> /dev/null; then
    echo "正在安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew 已安装"
    echo "正在更新 Homebrew..."
    brew update
fi

# 安装 libimobiledevice 和相关工具
echo "正在安装 libimobiledevice 和相关工具..."
brew install libimobiledevice

# 安装 ideviceinstaller
echo "正在安装 ideviceinstaller..."
brew install ideviceinstaller

# 安装 ios-deploy
echo "正在安装 ios-deploy..."
brew install ios-deploy

# 安装 carthage (WebDriverAgent 依赖)
echo "正在安装 carthage..."
brew install carthage

# 检查 Node.js 是否已安装
if ! command -v node &> /dev/null; then
    echo "正在安装 Node.js..."
    brew install node
else
    echo "✅ Node.js 已安装"
fi

# 检查 Appium 是否已安装
if ! command -v appium &> /dev/null; then
    echo "正在安装 Appium..."
    npm install -g appium
else
    echo "✅ Appium 已安装"
fi

# 检查 XCUITest 驱动程序是否已安装
echo "正在检查 XCUITest 驱动程序..."
appium driver list --installed

echo "正在安装 XCUITest 驱动程序..."
appium driver install xcuitest

echo "===== 依赖项安装完成 ====="
echo "现在你可以运行 ./check_wda.py 来检查和安装 WebDriverAgent"