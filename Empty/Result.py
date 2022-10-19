from functools import singledispatch


class Result:
    code = 0
    msg = ''
    data = object
    host = 'http://127.0.0.1:8000'
    def succ3(code, msg, datas):
        i = Result()
        i.msg = msg
        i.code = code
        i.data = datas
        return i

    def succ1(datas):
        i = Result()
        i.msg = "请求成功"
        i.code = 200
        i.data = datas
        return i

    def succ(*args):
        if len(args) == 1:
            return Result.succ1(args)
        elif len(args) == 3:
            return Result.succ3(args)

    def toString(std):
        return {
            'code': std.code,
            'msg': std.msg,
            'data': std.data
        }
