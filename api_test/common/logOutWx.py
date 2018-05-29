import itchat


def logout_wechat():
    """
    退出微信
    :return:
    """
    itchat.auto_login(hotReload=True)
    itchat.logout()
    return True
