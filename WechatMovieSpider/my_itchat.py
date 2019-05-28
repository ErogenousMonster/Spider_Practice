import itchat
import my_web_search


@itchat.msg_register(itchat.content.TEXT)
def simple_reply(msg):
    if u'电影' in msg['Text']:
        itchat.send_msg('等下厚，让本可找找惹。', msg['FromUserName'])
        douban_object.start_web_server()
        movie_category_msg = ' '.join(douban_object.category)
        itchat.send_msg('----请选择一种类型惹----\n' + movie_category_msg, msg['FromUserName'])
    elif msg['Text'] in douban_object.category:
        itchat.send_msg('正在查找' + msg['Text'] + '电影惹，嘻嘻嘻...', msg['FromUserName'])
        douban_object.start_explore_web_server()
        # 传入要搜索的电影类型
        douban_object.search_type = msg['Text']
        # 获取排名前十的电影列表
        movie_info_all = douban_object.get_specific_type_rank()
        # 如果成功获取数据
        if movie_info_all:
            itchat.send_msg('----按热度排序----\n' + '\n'.join(movie_info_all[0]), msg['FromUserName'])
            itchat.send_msg('----按时间排序----\n' + '\n'.join(movie_info_all[1]), msg['FromUserName'])
            itchat.send_msg('----按评论排序----\n' + '\n'.join(movie_info_all[2]), msg['FromUserName'])
        # 如果用户输入了错误的电影类型
        else:
            itchat.send_msg('请输入正确的电影类型惹：\n' + ' '.join(douban_object.category), msg['FromUserName'])
    else:
        itchat.send_msg('惹！请输入“看电影”，靴靴！', msg['FromUserName'])


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, enableCmdQR=1)
    douban_object = my_web_search.DoubanSpider()
    itchat.run()
