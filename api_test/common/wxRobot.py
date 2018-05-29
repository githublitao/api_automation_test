import itchat


def test_connect_wechat(data, name, _type):
    """
    测试连接微信
    :param data: 发送内容
    :param name: 发送目标人
    :param _type: 群或个人 group/person
    :return:
    """
    itchat.auto_login(hotReload=True)
    if _type == "group":
        users = itchat.search_chatrooms(name=name)
    else:
        users = itchat.search_friends(name=name)
    if len(users):
        use_name = users[0]['UserName']
        itchat.send(data, toUserName=use_name)
        return True
    else:
        return False
