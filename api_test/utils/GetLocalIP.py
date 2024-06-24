# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: GetLocalIP.py

# @Software: PyCharm

import socket


def get_local_ip():
    """
    获取当前服务器IP
    :return:
    """
    local_ip = ""
    try:
        socket_objs = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
        ip_from_ip_port = [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in socket_objs][0][1]
        ip_from_host_name = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if
                             not ip.startswith("127.")][:1]
        local_ip = [l for l in (ip_from_ip_port, ip_from_host_name) if l][0]
    except (Exception) as e:
        print("get_local_ip found exception : %s" % e)
    return local_ip if ("" != local_ip and None != local_ip) else socket.gethostbyname(socket.gethostname())


if __name__ == "__main__":
    print(socket.gethostname())
    print(socket.gethostbyname(socket.gethostname()))
    print(get_local_ip())

