version_file = "version.txt"

# 读取当前版本
with open(version_file, "r") as f:
    version = f.read().strip()

# 解析版本号（格式是 X.Y.Z）
major, minor, patch = map(int, version.split("."))

# 递增小版本号
new_version = f"{major}.{minor}.{patch + 1}"

# 写回 `version.txt`
with open(version_file, "w") as f:
    f.write(new_version)

print(f"Updated version: {new_version}")
