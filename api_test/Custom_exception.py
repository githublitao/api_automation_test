
class ParameterWrong(Exception):
    def __init__(self, err='参数有误'):
        Exception.__init__(self, err)


