import requests
from bs4 import BeautifulSoup
import yaml
import re
from datetime import datetime
import time


# 主函数
def main():
    # Zhicheng Dou的dblp页面URL
    dblp_url = "https://dblp.org/pid/18/5740.html"
    
    # get html page and save to file
    response = requests.get(dblp_url)
    with open("zhicheng_dou.html", "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    main()