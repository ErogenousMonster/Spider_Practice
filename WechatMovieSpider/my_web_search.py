import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep


movie_category = ['热门', '最新', '经典', '可播放', '豆瓣高分', '冷门佳片', '华语',
                  '欧美', '韩国', '日本', '动作', '喜剧', '爱情', '科幻', '悬疑',
                  '恐怖', '治愈']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3729.169 Safari/537.36'
}
# movie_info_hot = []
# movie_info_time = []
# movie_info_comment = []


class DoubanSpider:

    def __init__(self):
        self.category = movie_category
        self.base_url = 'https://movie.douban.com/'
        self.explore_url = 'https://movie.douban.com/explore'
        self.driver = webdriver.Chrome()
        self.search_type = None

    def start_web_server(self):
        self.driver.get(self.base_url)
        sleep(1)

    def start_explore_web_server(self):
        self.driver.get(self.explore_url)
        sleep(1)

    def get_specific_type_rank(self):
        if self.search_type:
            try:
                search_type_idx = movie_category.index(self.search_type) + 1
                self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[2]/div[1]/form/div[1]/div[1]/'
                                                  'label[{}]'.format(search_type_idx)).click()
                sleep(1)
                for counter in range(1, 4):
                    if counter == 1:
                        movie_info_hot = self.turn_list_to_msg(self.get_top_ten_movie_info(counter))
                    if counter == 2:
                        movie_info_time = self.turn_list_to_msg(self.get_top_ten_movie_info(counter))
                    if counter == 3:
                        movie_info_comment = self.turn_list_to_msg(self.get_top_ten_movie_info(counter))

                return [movie_info_hot, movie_info_time, movie_info_comment]
            except ValueError:
                # 表示用户输入了错误的电影类型
                return None

    def get_top_ten_movie_info(self, counter):
        self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[2]/div[1]/form/div[3]/div[1]'
                                          '/label[{}]/input'.format(counter)).click()
        sleep(1)
        top_ten_movie_info = []
        for x in range(1, 11):
            top_ten_movie_info.append(
                self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[4]/div/a[{}]/p'
                                                  .format(x)).text)
        return top_ten_movie_info

    @staticmethod
    def turn_list_to_msg(turn_list):
        turn_msg = []
        for turn_idx in range(len(turn_list)):
            turn_msg.append(str(turn_idx + 1) + '.' + turn_list[turn_idx].replace(' ', ' : ') + '分')
        return turn_msg


if __name__ == '__main__':
    douban_object = DoubanSpider()
    douban_object.start_explore_web_server()
    douban_object.search_type = '科幻'
    douban_object.get_specific_type_rank()
