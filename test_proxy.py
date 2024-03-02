import requests
from requests.exceptions import SSLError

course_page_url = 'https://selearning.nju.edu.cn/course/view.php?id=69'

try:
    # 假设你已经有了代理设置
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }

    # 发送请求
    response = requests.get(course_page_url, proxies=proxies)
    # 其他你的代码...
    print(response.text)
except SSLError as e:
    print(e)
