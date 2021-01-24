# -*- coding=utf-8 -*- #
# @author；zhangyihao
# @date: 2021-01

'''爬取指定网站的讲座信息并保存至本地

功能介绍
1. Selenium框架
2. 全部/指定网站爬取
3. 接口支持后期拓展


Typical usage example:

sp=SpiderMan()
sp.scrapy()

'''
from selenium import webdriver
import requests
import pandas as pd
import time
import os
from bs4 import BeautifulSoup
import warnings
import argparse
warnings.filterwarnings("ignore")

# TODO(zhangyihao.kevin@foxmail.com):
#  1. 定时爬虫
#  2. 详细信息精准提取

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome', type=str, default='./chromedriver.exe')
    # sjtu_law_seminar, ecupl_seminar, ecupl_gjf_seminar, shupl_seminar
    # sufe_law_seminar, ecupl_ipschool_seminar, shu_law_seminar, lawyers_seminar
    parser.add_argument('--target_web',type=str,default='shu_law_seminar')  #
    parser.add_argument('--if_all', type=bool, default=False)
    args = parser.parse_known_args()[0]
    return args

class SpiderMan(object):
    def __init__(self,args=get_args()):
        self.target_web=args.target_web
        self.if_all = args.if_all # 是否一次性爬所有网站
        self.driver= webdriver.Chrome(args.chrome)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',}
        self.driver.implicitly_wait(10)
        self.chrome=args.chrome

    def scrapy(self):
        if self.if_all:
            pass
        else:
            if self.target_web is 'sjtu_law_seminar':
                case_url='https://law.sjtu.edu.cn/Article0903_0.aspx' # 确保可以打开，否则请更改
                url = 'https://law.sjtu.edu.cn/Article0903_{}.aspx'
                self.sjtu_law_seminar(url,pages=2)    # 请指定爬取页数

            elif self.target_web is 'ecupl_seminar':
                case_url = 'https://www.ecupl.edu.cn/649/list1.htm'
                url = 'https://www.ecupl.edu.cn/649/list{}.htm'
                self.ecupl_seminar(url,pages=2)

            elif self.target_web is 'ecupl_gjf_seminar':
                case_url = 'https://gjf.ecupl.edu.cn/8595/list.htm'
                url = 'https://gjf.ecupl.edu.cn/8595/list{}.htm'
                self.ecupl_gjf_seminar(url,pages=2) # 翻页

            elif self.target_web is 'shupl_seminar':
                case_url='http://www.shupl.edu.cn/1219/list.htm'
                url='http://www.shupl.edu.cn/1219/list{}.htm'
                self.shupl_seminar(url,pages=2)

            elif self.target_web is 'sufe_law_seminar':
                case_url = 'http://law.sufe.edu.cn/jzyg2/list.htm'
                url = 'http://law.sufe.edu.cn/jzyg2/list{}.htm'
                self.sufe_law_seminar(url,pages=2)

            elif self.target_web is 'ecupl_ipschool_seminar':
                case_url = 'https://ipschool.ecupl.edu.cn/3962/list.htm'
                url = 'https://ipschool.ecupl.edu.cn/3962/list{}.htm'
                self.ecupl_ipschool_seminar(url,pages=2)

            elif self.target_web is 'shu_law_seminar':
                case_url = 'https://law.shu.edu.cn/zxzx/jzhyth.htm'
                url = 'https://law.shu.edu.cn/zxzx/jzhyth.htm'
                self.shu_law_seminar(url)  # 只读第一页

            else:
                case_url = 'http://www.lawyers.org.cn/member/unionnotice?currentPageNo=1'
                url = 'http://www.lawyers.org.cn/member/unionnotice?currentPageNo={}'
                self.lawyers_seminar(url,pages=2) # 翻页

    def sjtu_law_seminar(self,url: str, pages: int) -> None:
        """爬取上海交通大学法学院讲座信息

        Args：
        url:
            网站地址
        pages:
            需要爬的页数

        Returns:
            None
        """
        count = 0
        organizer = '上海交通大学凯源法学院'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, post_dates, presenters,pre_dates, addresses = [], [],[],[],[],[],[]
        other_webs,others_titles=[],[]
        for num in range(1,pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            mainWindow = self.driver.current_window_handle
            elements = self.driver.find_elements_by_css_selector('.body1 li')
            if not elements:
                print('该网站布局改变，跳过！！')
                continue
            else:
                for ele in elements:
                    times = ele.find_elements_by_css_selector('.box_r')
                    titles = ele.find_elements_by_css_selector('a')
                    for ind, _ in enumerate(titles):
                        flag=0
                        # 【会议】、【研讨会】只保存网站url和标题
                        if titles[ind].text.startswith('【会议】') or titles[ind].text.startswith('【研讨会】'):
                            other_webs.append(url.format(num))
                            others_titles.append(titles[ind].text)
                            continue

                        # search in page
                        print(titles[ind].text)  # 标题
                        try:
                            self.driver.find_element_by_css_selector("[title='{}']".format(titles[ind].text)).click()
                            #css="//*[starts-with(text(),'{}')]".format(titles[ind].text)
                            #print(css)
                            #self.driver.find_element_by_css_selector(css).click()
                        except Exception:
                            title_text = titles[ind].text
                            cnt=0
                            while True:
                                title_text = title_text + ' '
                                cnt+=1
                                m=self.driver.find_elements_by_css_selector("[title='{}']".format(title_text))
                                if not m:
                                    if cnt >= 4:
                                        flag=1
                                        break
                                    else:
                                        continue
                                else:
                                    m[0].click()
                                    break
                            #css = "//*[starts-with(text(),'{}')]".format(titles[ind].text)
                            #print(css)
                            #self.driver.find_element_by_css_selector(css).click()
                        if flag==1:
                            continue
                        titles_.append(titles[ind].text)
                        post_dates.append(times[ind].text)
                        count += 1
                        ids.append(count)
                        organizers.append(organizer)
                        self.driver.switch_to.window(self.driver.window_handles[1])  # 所有打开的窗口中的第1个
                        # print(self.driver.current_url)
                        time.sleep(2)

                        ######### 主讲人特殊处理 #######
                        try:
                            speaker = self.driver.find_element_by_xpath("//*[starts-with(text(),'主讲')]")
                            presenters.append(speaker.text.split('：')[1])
                        except Exception:
                            speaker_father = self.driver.find_elements_by_xpath(
                                "//span[1 and starts-with(text(),'主')]/..")
                            if not speaker_father:
                                print('no speaker')
                                presenters.append('NAN')
                            else:
                                father_sons = speaker_father[0].find_elements_by_xpath("span")
                                content = ''
                                if len(father_sons) == 1:
                                    # 包装在span下的 多个span里
                                    speaker_father_sons = father_sons[0].find_elements_by_xpath("span")
                                    for so in speaker_father_sons:
                                        content = content + so.text
                                else:
                                    for line in father_sons:
                                        content = content + line.text
                                presenters.append(content)

                        ######### 时间特殊处理 #######
                        try:
                            pre_date = self.driver.find_element_by_xpath(
                                "//*[starts-with(text(),'时间') or starts-with(text(),'讲座时间') or contains(text(),'间：')]")
                            pre_dates.append(pre_date.text.split('：')[1])
                        except Exception:
                            speaker_father = self.driver.find_elements_by_xpath(
                                "//span[1 and starts-with(text(),'时')]/..")
                            if not speaker_father:
                                print('no time')
                                pre_dates.append('NAN')
                            else:
                                father_sons = speaker_father[0].find_elements_by_xpath("span")
                                content = ''
                                if len(father_sons) == 1:
                                    # 包装在span下的 多个span里
                                    speaker_father_sons = father_sons[0].find_elements_by_xpath("span")
                                    for so in speaker_father_sons:
                                        content = content + so.text
                                else:
                                    for line in father_sons:
                                        content = content + line.text
                                pre_dates.append(content)

                        ######### 地点特殊处理 #######
                        try:
                            address = self.driver.find_element_by_xpath("//*[contains(text(),'地点')]")  # starts-with
                            addresses.append(address.text.split('：')[1])
                        except Exception:
                            speaker_father = self.driver.find_elements_by_xpath(
                                "//span[1 and contains(text(),'地')]/..")  # starts-with
                            if not speaker_father:
                                print('no place')
                                addresses.append('NAN')
                            else:
                                father_sons = speaker_father[0].find_elements_by_xpath("span")
                                content = ''
                                if len(father_sons) == 1:
                                    # 包装在span下的 多个span里
                                    speaker_father_sons = father_sons[0].find_elements_by_xpath("span")
                                    for so in speaker_father_sons:
                                        content = content + so.text
                                else:
                                    for line in father_sons:
                                        content = content + line.text
                                addresses.append(content)
                        print(len(ids),len(organizers),len(titles_),len(post_dates),len(presenters),len(pre_dates),len(addresses))
                        self.driver.close()
                        self.driver.switch_to.window(mainWindow)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': post_dates,
                '主讲人': presenters, '讲座日期': pre_dates, '讲座地址': addresses}
        res=pd.DataFrame(data)
        res.to_csv(os.path.join('data','{}_results.csv'.format(self.target_web)))
        print(res)

        other_data={'标题':others_titles,'网址':other_webs}
        other_res = pd.DataFrame(other_data)
        print(other_res)
        other_res.to_csv(os.path.join('data','{}_other_results.csv'.format(self.target_web)))
        self.driver.quit()

    def ecupl_seminar(self,url: str, pages: int) -> None:
        count = 0
        organizer = '华东政法大学官网'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, post_dates, contents = [], [], [], [], []
        for num in range(1, pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            mainWindow = self.driver.current_window_handle
            elements = self.driver.find_elements_by_css_selector('.list_item')
            for ele in elements:
                times = ele.find_elements_by_css_selector('.Article_PublishDate')
                titles = ele.find_elements_by_css_selector('.Article_Title')
                for ind, _ in enumerate(titles):
                    # search in page
                    print(titles[ind].text)  # 标题
                    titles_.append(titles[ind].text)
                    post_dates.append(times[ind].text)
                    count += 1
                    ids.append(count)
                    organizers.append(organizer)

                    # path="//*[starts-with(@title,'{}')]".format(titles[ind].text)
                    '''
                    此处应该用find_element_by_xpath  而不是  find_element_by_css_selector
                    '''
                    try:
                        self.driver.find_element_by_xpath("//*[starts-with(@title,'{}')]".format(titles[ind].text)).click()
                    except Exception:
                        part_title=titles[ind].text[:42]
                        self.driver.find_element_by_xpath(
                            "//*[starts-with(@title,'{}')]".format(part_title)).click()
                    time.sleep(1)
                    # self.driver.find_element_by_css_selector(
                    #     "[title='{}']".format(titles[ind].text)).click()
                    # time.sleep(1)
                    hand= self.driver.window_handles
                    self.driver.switch_to.window(hand[1]) # 切换到最高句柄
                    currentPageUrl = self.driver.current_url

                    html_ = requests.get(currentPageUrl, headers=self.headers)
                    html_.encoding = 'utf-8'
                    text = html_.text
                    soup = BeautifulSoup(text, 'html.parser')
                    lines = soup.find_all('div', class_='wp_articlecontent')
                    contents.append(lines[0].text)
                    self.driver.close()
                    self.driver.switch_to.window(mainWindow)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': post_dates,'内容': contents}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data','{}_results.csv'.format(self.target_web)))
        self.driver.quit()

    def ecupl_gjf_seminar(self, url: str, pages: int):
        count = 0
        organizer = '华东政法大学国际法学院'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, post_dates, contents = [], [], [], [], []
        mainWindow = self.driver.current_window_handle
        mainPageUrl = self.driver.current_url
        for num in range(1, pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            elements = self.driver.find_elements_by_css_selector('h3 a')
            for ind,ele in enumerate(elements):  # 对于不弹窗的网页，需要解决页面刷新的问题
                title = ele.text
                print(title)
                titles_.append(title)
                count += 1
                ids.append(count)
                organizers.append(organizer)
            self.driver.close()
            print('**********************')
            for val in titles_:
                print(val)
                self.driver = webdriver.Chrome(self.chrome)
                self.driver.get(url.format(num))
                self.driver.find_element_by_css_selector(
                    "[title='{}']".format(val)).click()
                time.sleep(1)
                hand = self.driver.window_handles
                self.driver.switch_to.window(hand[0])  # 切换到最高句柄
                currentPageUrl = self.driver.current_url

                html_ = requests.get(currentPageUrl, headers=self.headers)
                html_.encoding = 'utf-8'
                text = html_.text
                soup = BeautifulSoup(text, 'html.parser')
                lines = soup.find_all('div', class_='wp_articlecontent')
                try:
                    contents.append(lines[0].text)
                except Exception:
                    contents.append([])
                self.driver.close()
                #self.driver.switch_to.window(mainWindow)
                #self.driver.get(url.format(num))
                #time.sleep(1)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '内容': contents}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data','{}_results.csv'.format(self.target_web)))
        self.driver.quit()

    def shupl_seminar(self,url,pages):
        count = 0
        organizer = '上海政法学院'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, post_dates, contents = [], [], [], [], []
        for num in range(1, pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            mainWindow = self.driver.current_window_handle
            elements = self.driver.find_elements_by_xpath('//*[starts-with(@class,"column-news-item")]')
            for ele in elements:
                times = ele.find_elements_by_xpath('./span[2]') ## 必须要加.  否则是从全局找
                titles = ele.find_elements_by_xpath('./span[1]')
                for ind, _ in enumerate(titles):
                    # search in page
                    print(titles[ind].text)  # 标题
                    titles_.append(titles[ind].text)
                    post_dates.append(times[ind].text)
                    print(times[ind].text)
                    count += 1
                    ids.append(count)
                    organizers.append(organizer)

                    try:
                        self.driver.find_element_by_xpath(
                            "//*[starts-with(text(),'{}')]".format(titles[ind].text)).click()
                    except Exception:
                        part_title = titles[ind].text[:42]  # 如果超过42个字符，取前42位
                        self.driver.find_element_by_xpath(
                            "//*[starts-with(text(),'{}')]".format(part_title)).click()
                    time.sleep(1)
                    # self.driver.find_element_by_css_selector(
                    #     "[title='{}']".format(titles[ind].text)).click()
                    # time.sleep(1)
                    hand = self.driver.window_handles
                    self.driver.switch_to.window(hand[1])  # 切换到最高句柄
                    currentPageUrl = self.driver.current_url

                    html_ = requests.get(currentPageUrl, headers=self.headers)
                    html_.encoding = 'utf-8'
                    text = html_.text
                    soup = BeautifulSoup(text, 'html.parser')
                    lines = soup.find_all('div', class_='wp_articlecontent')
                    contents.append(lines[0].text)
                    self.driver.close()
                    self.driver.switch_to.window(mainWindow)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': post_dates, '内容': contents}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data','{}_results.csv'.format(self.target_web)))
        self.driver.quit()

    def sufe_law_seminar(self,url,pages):
        count = 0
        organizer = '上海财经大学法学院'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, post_dates, contents = [], [], [], [], []
        for num in range(1, pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            mainWindow = self.driver.current_window_handle
            whole=self.driver.find_element_by_css_selector('[class="news_list list2"]')
            elements = whole.find_elements_by_css_selector("li[class^='news']")
            for ele in elements:
                titles = ele.find_elements_by_css_selector('.news_title')
                times = ele.find_elements_by_css_selector('.news_meta')
                for ind, _ in enumerate(titles):
                    # search in page
                    print(titles[ind].text)  # 标题
                    titles_.append(titles[ind].text)
                    post_dates.append(times[ind].text)
                    print(times[ind].text)
                    count += 1
                    ids.append(count)
                    organizers.append(organizer)
                    # try:
                    #     self.driver.find_element_by_xpath(
                    #         "//*[starts-with(text(),'{}')]".format(titles[ind].text)).click()
                    # except Exception:
                    #     part_title = titles[ind].text[:42]  # 如果超过42个字符，取前42位
                    #     self.driver.find_element_by_xpath(
                    #         "//*[starts-with(text(),'{}')]".format(part_title)).click()
                    self.driver.find_element_by_css_selector(
                        "[title='{}']".format(titles[ind].text)).click()
                    time.sleep(1)
                    hand = self.driver.window_handles
                    self.driver.switch_to.window(hand[1])  # 切换到最高句柄
                    currentPageUrl = self.driver.current_url

                    html_ = requests.get(currentPageUrl, headers=self.headers)
                    html_.encoding = 'utf-8'
                    text = html_.text
                    soup = BeautifulSoup(text, 'html.parser')
                    lines = soup.find_all('div', class_='wp_articlecontent')
                    contents.append(lines[0].text)
                    self.driver.close()
                    self.driver.switch_to.window(mainWindow)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': post_dates, '内容': contents}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data', '{}_results.csv'.format(self.target_web)))
        self.driver.quit()

    def ecupl_ipschool_seminar(self,url,pages):
        count = 0
        organizer = '华东政法大学知识产权学院'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, post_dates, contents = [], [], [], [], []
        for num in range(1, pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            mainWindow = self.driver.current_window_handle
            elements = self.driver.find_elements_by_css_selector('[id="wp_news_w05"] li')
            for num,ele in enumerate(elements):
                titles = ele.find_elements_by_css_selector('[title]')
                times = ele.find_elements_by_css_selector('span')  ## 必须要加.  否则是从全局找
                for ind, _ in enumerate(titles):
                    # search in page
                    print(titles[ind].text)  # 标题
                    titles_.append(titles[ind].text)
                    post_dates.append(times[ind].text)
                    print(times[ind].text)
                    count += 1
                    ids.append(count)
                    organizers.append(organizer)
                    try:
                        self.driver.find_element_by_css_selector(
                             "[title='{}']".format(titles[ind].text)).click()
                    except Exception:
                        ele.find_element_by_css_selector("a:nth-of-type(2)").click()
                    time.sleep(1)
                    hand = self.driver.window_handles
                    self.driver.switch_to.window(hand[1])  # 切换到最高句柄
                    currentPageUrl = self.driver.current_url

                    html_ = requests.get(currentPageUrl, headers=self.headers)
                    html_.encoding = 'utf-8'
                    text = html_.text
                    soup = BeautifulSoup(text, 'html.parser')
                    lines = soup.find_all('div', class_='wp_articlecontent')
                    contents.append(lines[0].text)
                    self.driver.close()
                    self.driver.switch_to.window(mainWindow)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': post_dates, '内容': contents}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data', '{}_results.csv'.format(self.target_web)))
        self.driver.quit()

    def shu_law_seminar(self,url):
        count = 0
        organizer = '上海大学法学院'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址

        ids, organizers, titles_, post_dates, contents = [], [], [], [], []
        self.driver.get(url)
        elements = self.driver.find_elements_by_css_selector('.d-right-down ul li')
        for ind, ele in enumerate(elements):  # 对于不弹窗的网页，需要解决页面刷新的问题
            title = ele.find_element_by_css_selector('a').text
            time_ = ele.find_element_by_css_selector('span').text
            print(title)
            titles_.append(title)
            count += 1
            post_dates.append(time_)
            ids.append(count)
            organizers.append(organizer)

        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': post_dates,}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data', '{}_results.csv'.format(self.target_web)))
        self.driver.quit()

    def lawyers_seminar(self,url,pages):
        count = 0
        organizer = '东方律师'
        ## |编号|主办单位|标题|公告日期|主讲人|讲座日期|讲座地址
        ids, organizers, titles_, times_,post_dates, contents = [], [], [], [], [],[]
        for num in range(1, pages):
            print(url.format(num))
            self.driver.get(url.format(num))
            elements = self.driver.find_elements_by_css_selector('.g-left-hyfw .content ul li')
            for ind, ele in enumerate(elements):  # 对于不弹窗的网页，需要解决页面刷新的问题
                title = ele.find_element_by_css_selector('[title]').text
                time_ = ele.find_element_by_css_selector('.date').text
                print(title)
                titles_.append(title)
                times_.append(time_)
                count += 1
                ids.append(count)
                organizers.append(organizer)
            self.driver.close()
            print('**********************')
            for val in titles_:
                print(val)
                self.driver = webdriver.Chrome(self.chrome)
                self.driver.get(url.format(num))
                try:
                    self.driver.find_element_by_css_selector(
                        "[title='{}']".format(val)).click()
                except Exception:
                    part_title = val[:30]  # 如果超过30个字符，取前30位
                    self.driver.find_element_by_xpath(
                        "//*[starts-with(text(),'{}')]".format(part_title)).click()

                time.sleep(1)
                hand = self.driver.window_handles
                self.driver.switch_to.window(hand[0])  # 切换到最高句柄
                currentPageUrl = self.driver.current_url

                html_ = requests.get(currentPageUrl, headers=self.headers)
                html_.encoding = 'utf-8'
                text = html_.text
                soup = BeautifulSoup(text, 'html.parser')
                lines = soup.find_all('div', class_='info')
                try:
                    contents.append(lines[0].text)
                except Exception:
                    contents.append([])
                self.driver.close()
                # self.driver.switch_to.window(mainWindow)
                # self.driver.get(url.format(num))
                # time.sleep(1)
        # 数据保存
        data = {'编号': ids, '主办单位': organizers, '标题': titles_, '公告日期': times_,'内容': contents}
        res = pd.DataFrame(data)
        res.to_csv(os.path.join('data', '{}_results.csv'.format(self.target_web)))
        self.driver.quit()


if __name__=='__main__':
    sp=SpiderMan()
    sp.scrapy()