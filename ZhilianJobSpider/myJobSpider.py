import urllib
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pymysql
from os import _exit, system
from threading import Thread, Lock


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                  '537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/'
              '*;q=0.8,application/signed-exchange;v=b3'
}
city_list = ['北京', '上海', '广州', '深圳', '天津', '武汉', '西安', '成都', '大连', '长春', '沈阳', '南京'
                '济南', '青岛', '杭州', '苏州', '无锡', '宁波', '重庆', '郑州', '长沙', '福州', '厦门', '哈尔滨'
                '石家庄', '合肥', '惠州']


class ZLSpider:
    def __init__(self):
        self.base_url = 'https://sou.zhaopin.com/'
        self.target_url = None
        # 初始化数据库
        self.conn = pymysql.connect(host='localhost', user='root', password='root')
        self.cur = self.conn.cursor()
        self.cur.execute('use spider;')
        self.cur.execute('truncate table job;')

    @property
    def city_cmd_get(self):
        return self._city_name

    @city_cmd_get.setter
    def city_cmd_get(self, city_name_input):
        if city_name_input not in city_list:
            raise ValueError('请输入主要城市名称。')
        self._city_name = city_name_input

    @property
    def job_name_cmd_get(self):
        return self._job_name

    @job_name_cmd_get.setter
    def job_name_cmd_get(self, job_name_input):
        # 如果输入为空
        if not job_name_input:
            raise ValueError('请输入正确的关键词字符串。')
        self._job_name = job_name_input

    def get_target_url(self):
        target_url = self.base_url + '?p={}' + '&jl=' + urllib.parse.quote(self._city_name) + '&sf=0&st=0' + \
                          '&kw=' + urllib.parse.quote(self._job_name) + '&kt=3'

        return target_url

    def get_and_save_info(self, url):
        # 初始化driver
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(30)
        # 初始化base_url
        try:
            driver.get(self.base_url)
        except TimeoutException:
            print('网页连接超时，请重新连接。')
            driver.quit()
            system('pause')
            _exit(5)
        sleep(2)
        
        element = None
        try:
            driver.get(url)
        except TimeoutException:
            print('网页连接超时，请重新连接。')
            driver.quit()
            system('pause')
            _exit(5)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "listContent"))
            )

        finally:
            if element is None:
                print('没有找到相关信息。')
                driver.quit()
                system('pause')
                _exit(5)
            # except:
            #     print('网页链接超时，请检查网络连接再运行。')
            #     system('pause')
            #     _exit(5)
            number = len(driver.find_elements_by_xpath('//*[@id="listContent"]/'
                                                            'div[@class="contentpile__content__wrapper clearfix"]'))
            if number == 0:
                print('没有找到相关信息。')
                driver.quit()
                system('pause')
                _exit(5)

            # 获取数据并填入数据库中
            for num_idx in range(number):
                # div1
                job_name_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/div[1]/div[1]'
                                                                  '/span[1]'.format(num_idx + 1)).get_attribute('title')
                company_name_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/'
                                                        'div[1]/div[2]/a'.format(num_idx + 1)).get_attribute('title')
                # div2
                salary_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/div[2]/div[1]/p'.
                                                                     format(num_idx + 1)).text
                address_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/div[2]/div[1]/'
                                                                 'ul/li[1]'.format(num_idx + 1)).text
                education_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/div[2]/div[1]/'
                                                                   'ul/li[2]'.format(num_idx + 1)).text
                company_attribute_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/'
                                                                    'div[2]/div[2]/span[1]'.format(num_idx + 1)).text
                company_size_item = driver.find_element_by_xpath('//*[@id="listContent"]/div[{}]/div/a/div[2]/'
                                                                      'div[2]/span[2]'.format(num_idx + 1)).text
                # div3
                welfare_info = driver.find_elements_by_xpath('//*[@id="listContent"]/div[{}]/div/a/div[3]/div[1]/'
                                                                  'div'.format(num_idx + 1))
                welfare_info_list = [i.text for i in welfare_info]
                welfare_info_item = ','.join(welfare_info_list)
                # 填入数据库
                self.lock.acquire()
                print(job_name_item, salary_item, address_item, education_item, company_name_item,
                      company_attribute_item, company_size_item, welfare_info_item)
                self.cur.execute(
                'insert into job (job_name, salary, address, education, company_name, company_attribute, company_size,'
                'welfare) values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'.format(job_name_item,
                                                                                            salary_item,
                                                                                            address_item,
                                                                                            education_item,
                                                                                            company_name_item,
                                                                                            company_attribute_item,
                                                                                            company_size_item,
                                                                                            welfare_info_item))
                self.lock.release()

            driver.quit()

    def run(self):
        self._city_name = input('请输入工作地点：')
        self._job_name = input('请输入搜索工作名称：')

        # 创建多线程
        self.lock = Lock()
        html_thread_object = []
        for x in range(5):
            url = self.get_target_url().format(x + 1)
            html_thread_object.append(Thread(target=self.get_and_save_info, args=(url,)))

        for elem in html_thread_object:
            elem.start()
        for elem in html_thread_object:
            elem.join()
        self.conn.commit()


if __name__ == '__main__':
    mySpider = ZLSpider()
    mySpider.run()
