#!/usr/bin/env python3
"""
性能报告查看器
提供一个简单的Web界面来查看和管理生成的性能报告
"""

import os
import webbrowser
import http.server
import socketserver
import json
from datetime import datetime
import re
from urllib.parse import parse_qs, urlparse

# 报告目录
REPORTS_DIR = os.path.join(os.getcwd(), "performance_reports")

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>应用性能报告查看器</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .report-list {
            list-style: none;
            padding: 0;
        }
        .report-item {
            background-color: #f9f9f9;
            border-radius: 5px;
            margin-bottom: 15px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .report-info {
            flex: 1;
        }
        .report-title {
            font-size: 18px;
            font-weight: bold;
            margin: 0 0 5px 0;
            color: #3498db;
        }
        .report-meta {
            color: #7f8c8d;
            font-size: 14px;
        }
        .report-actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            display: inline-block;
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .btn-delete {
            background-color: #e74c3c;
        }
        .btn-delete:hover {
            background-color: #c0392b;
        }
        .filter-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            align-items: center;
        }
        .filter-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        select, input {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        .platform-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 8px;
        }
        .platform-ios {
            background-color: #a8d2ff;
            color: #0055b3;
        }
        .platform-android {
            background-color: #c8e6c9;
            color: #2e7d32;
        }
        .stats-container {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background-color: #fff;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>应用性能报告查看器</h1>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-label">总报告数</div>
            <div class="stat-value">{{total_reports}}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">iOS报告</div>
            <div class="stat-value">{{ios_reports}}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Android报告</div>
            <div class="stat-value">{{android_reports}}</div>
        </div>
    </div>
    
    <div class="filter-bar">
        <div class="filter-group">
            <label for="platform-filter">平台:</label>
            <select id="platform-filter" onchange="applyFilters()">
                <option value="all">全部</option>
                <option value="ios">iOS</option>
                <option value="android">Android</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="date-filter">日期:</label>
            <input type="date" id="date-filter" onchange="applyFilters()">
        </div>
        <div class="filter-group">
            <label for="search-filter">搜索:</label>
            <input type="text" id="search-filter" placeholder="应用包名..." oninput="applyFilters()">
        </div>
    </div>
    
    {{#if reports.length}}
    <ul class="report-list">
        {{#each reports}}
        <li class="report-item" data-platform="{{platform}}" data-date="{{date}}" data-package="{{package}}">
            <div class="report-info">
                <h3 class="report-title">
                    <span class="platform-badge platform-{{platform}}">{{platform}}</span>
                    {{title}}
                </h3>
                <div class="report-meta">
                    <span>{{date_formatted}}</span> | 
                    <span>{{package}}</span>
                </div>
            </div>
            <div class="report-actions">
                <a href="{{path}}" class="btn" target="_blank">查看报告</a>
                <button class="btn btn-delete" onclick="deleteReport('{{path}}')">删除</button>
            </div>
        </li>
        {{/each}}
    </ul>
    {{else}}
    <div class="empty-state">
        <p>暂无性能报告</p>
        <p>运行性能监控脚本生成报告</p>
    </div>
    {{/if}}
    
    <script>
        function applyFilters() {
            const platformFilter = document.getElementById('platform-filter').value;
            const dateFilter = document.getElementById('date-filter').value;
            const searchFilter = document.getElementById('search-filter').value.toLowerCase();
            
            document.querySelectorAll('.report-item').forEach(item => {
                const platform = item.dataset.platform;
                const date = item.dataset.date;
                const packageName = item.dataset.package.toLowerCase();
                
                const platformMatch = platformFilter === 'all' || platform === platformFilter;
                const dateMatch = !dateFilter || date === dateFilter;
                const searchMatch = !searchFilter || packageName.includes(searchFilter);
                
                if (platformMatch && dateMatch && searchMatch) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        function deleteReport(path) {
            if (confirm('确定要删除此报告吗？')) {
                fetch(`/delete?path=${encodeURIComponent(path)}`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            alert('删除失败: ' + data.error);
                        }
                    })
                    .catch(error => {
                        alert('删除请求失败: ' + error);
                    });
            }
        }
    </script>
</body>
</html>
"""


class ReportViewerHandler(http.server.SimpleHTTPRequestHandler):
    """处理报告查看器的HTTP请求"""

    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)

        # 处理根路径请求，显示报告列表
        if parsed_url.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # 获取报告列表
            reports = self.get_reports()

            # 统计数据
            total_reports = len(reports)
            ios_reports = sum(1 for r in reports if r["platform"] == "ios")
            android_reports = sum(1 for r in reports if r["platform"] == "android")

            # 渲染HTML
            html = self.render_template(
                HTML_TEMPLATE,
                {
                    "reports": reports,
                    "total_reports": total_reports,
                    "ios_reports": ios_reports,
                    "android_reports": android_reports,
                },
            )

            self.wfile.write(html.encode("utf-8"))
            return

        # 处理静态文件请求
        return super().do_GET()

    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)

        # 处理删除报告请求
        if parsed_url.path == "/delete":
            query = parse_qs(parsed_url.query)
            path = query.get("path", [""])[0]

            response = {"success": False}

            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    response = {"success": True}
                except Exception as e:
                    response = {"success": False, "error": str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def get_reports(self):
        """获取所有性能报告"""
        reports = []

        if not os.path.exists(REPORTS_DIR):
            return reports

        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith(".html"):
                file_path = os.path.join(REPORTS_DIR, filename)

                # 解析文件名获取信息
                platform = "ios"
                if "android" in filename:
                    platform = "android"

                # 尝试从文件名中提取日期和时间
                date_match = re.search(r"(\d{8})_(\d{6})", filename)
                if date_match:
                    date_str = date_match.group(1)
                    time_str = date_match.group(2)
                    date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                else:
                    # 使用文件修改时间作为备选
                    mtime = os.path.getmtime(file_path)
                    date_formatted = datetime.fromtimestamp(mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

                # 尝试从文件名中提取包名
                package_match = re.search(r"com\.\w+\.\w+", filename)
                package = package_match.group(0) if package_match else "未知应用"

                # 创建报告标题
                title = f"性能报告 - {date_formatted}"

                reports.append(
                    {
                        "path": file_path,
                        "title": title,
                        "date": date,
                        "date_formatted": date_formatted,
                        "platform": platform,
                        "package": package,
                    }
                )

        # 按日期降序排序
        reports.sort(key=lambda x: x["date_formatted"], reverse=True)

        return reports

    def render_template(self, template, context):
        """简单的模板渲染函数"""
        # 处理条件语句
        if_pattern = r"{{#if ([^}]+)}}(.*?){{else}}(.*?){{/if}}"
        for match in re.finditer(if_pattern, template, re.DOTALL):
            condition = match.group(1)
            if_block = match.group(2)
            else_block = match.group(3)

            # 评估条件
            try:
                condition_value = eval(condition, {}, context)
                replacement = if_block if condition_value else else_block
                template = template.replace(match.group(0), replacement)
            except Exception:
                template = template.replace(match.group(0), "")

        # 处理简单的if语句（没有else）
        if_pattern = r"{{#if ([^}]+)}}(.*?){{/if}}"
        for match in re.finditer(if_pattern, template, re.DOTALL):
            condition = match.group(1)
            if_block = match.group(2)

            # 评估条件
            try:
                condition_value = eval(condition, {}, context)
                replacement = if_block if condition_value else ""
                template = template.replace(match.group(0), replacement)
            except Exception:
                template = template.replace(match.group(0), "")

        # 处理循环
        each_pattern = r"{{#each ([^}]+)}}(.*?){{/each}}"
        for match in re.finditer(each_pattern, template, re.DOTALL):
            array_name = match.group(1)
            item_template = match.group(2)

            try:
                array = eval(array_name, {}, context)
                replacements = []

                for item in array:
                    item_html = item_template
                    # 替换项目中的变量
                    for key, value in item.items():
                        item_html = item_html.replace("{{" + key + "}}", str(value))
                    replacements.append(item_html)

                template = template.replace(match.group(0), "".join(replacements))
            except Exception:
                template = template.replace(match.group(0), "")

        # 替换变量
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                template = template.replace("{{" + key + "}}", str(value))

        return template


def start_server(port=8000):
    """启动HTTP服务器"""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 设置处理程序
    handler = ReportViewerHandler
    handler.directory = os.getcwd()

    # 创建服务器
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"报告查看器服务器启动在 http://localhost:{port}")
        print("按 Ctrl+C 停止服务器")

        # 打开浏览器
        webbrowser.open(f"http://localhost:{port}")

        try:
            # 启动服务器
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    # 解析命令行参数
    import argparse

    parser = argparse.ArgumentParser(description="性能报告查看器")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口号")
    args = parser.parse_args()

    # 启动服务器
    start_server(args.port)
