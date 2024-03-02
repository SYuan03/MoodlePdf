import os
import re
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

# ANSI 转义序列
GREEN = '\033[92m'
RESET = '\033[0m'

# 课程页面的URL
course_page_url = 'https://selearning.nju.edu.cn/course/view.php?id=72'

# 假设你已经有了代理设置
# proxies = {
#     'http': 'http://127.0.0.1:7890',
#     'https': 'http://127.0.0.1:7890',
# }

cookies = {
    # 应该创个.env存的，懒得写了
    "MoodleSession": "5c81tiktsueu5fbti0a66o9oki",
}

# 开始会话
session = requests.Session()
session.cookies.update(cookies)

# 获取课程页面的HTML内容
# course_page = session.get(course_page_url, proxies=proxies)
course_page = session.get(course_page_url)

course_page_html = course_page.text

# 将HTML内容保存到文件
with open("course_page.html", "w", encoding="utf-8") as f:
    f.write(course_page_html)
# 打印保存成功信息
print(f"{GREEN}course_page.html saved successfully{RESET}")

# 解析HTML内容
soup = BeautifulSoup(course_page_html, 'html.parser')
# 假设所有的PDF文件链接包含在<a>标签中并且有特定的class
# 注意：你需要检查网页源代码来确认正确的类名或其他属性
pdf_links = soup.find_all('a', class_='aalink')

# 用于存储PDF文件的目录
# 找到<div>标签并提取<h1>标签内的文本
page_header = soup.find('div', class_='page-header-headings')
course_title = page_header.h1.text if page_header else 'Default_Course_Title'

# 清理文件名（移除可能导致问题的字符）
invalid_chars = '[<>:"/\\|?*\']|[\0-\31]'
# 使用正则表达式替换上述无效字符为空字符串
safe_course_title = re.sub(invalid_chars, '', course_title)
download_dir = "xiazai-" + safe_course_title
print(f"Saving PDFs to {download_dir}")

# 确保下载目录存在
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# 遍历所有找到的PDF链接
for link in pdf_links:
    # 获取课程资源的链接（可能是一个跳转页面）
    resource_url = link['href']

    # 如果链接是跳转到下载页面的链接
    if "resource/view.php" in resource_url:
        # 获取跳转页内容
        # resource_page = session.get(resource_url, allow_redirects=True, proxies=proxies)
        resource_page = session.get(resource_url, allow_redirects=True)

        # 服务器可能会进行重定向，所以我们获取最终的URL
        pdf_url = resource_page.url

        # 检查URL是否指向一个PDF文件
        if pdf_url.endswith('.pdf'):
            pdf_filename = os.path.basename(pdf_url)

            # 下载PDF文件
            # pdf_response = session.get(pdf_url, stream=True, proxies=proxies)
            pdf_response = session.get(pdf_url, stream=True)

            # 确保请求成功
            if pdf_response.status_code == 200:
                # 对URL中的文件名进行解码
                decoded_filename = unquote(os.path.basename(pdf_url))
                pdf_path = os.path.join(download_dir, decoded_filename)
                with open(pdf_path, 'wb') as f:
                    for chunk in pdf_response.iter_content(chunk_size=128):
                        f.write(chunk)
                print(f"Downloaded {decoded_filename}")
            else:
                print(f"Failed to download {decoded_filename}")
        else:
            print(f"Skipping {pdf_url} (not a PDF file)")

# 结束会话
session.close()
