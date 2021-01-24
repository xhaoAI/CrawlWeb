# CrawlWeb

This repository is a tool for simple website crawling by analyzing source code (**html**) and web structure (js)

主要工具：

- selenium
- beatifulsoup4
- Chromedriver



爬取网站：

- 讲座标题（标题，时间，学校）
- 讲座内容（主讲人，讲座时间，讲座内容等）



## Start
1. 安装requirement.txt
2. run main.py
3. 运行前需要修改get_args函数里的参数：target_web：你想要爬的网站
4. 修改scrapy函数里的pages。默认pages=2表示只爬第一页