"""一个刻意埋了问题的测试文件，用来验证代码审查 Agent。"""


def calc(x, y, op):
    """执行运算，op 可以是 'add' 'sub' 'mul' 'div'"""
    if op == "add":
        return x + y
    if op == "sub":
        return x - y
    if op == "mul":
        return x * y
    if op == "div":
        return x / y
    return None


def find_max(lst):
    max_val = lst[0]
    for i in range(1, len(lst)):
        if lst[i] < max_val:
            max_val = lst[i]
    return max_val


def process_data(data):
    result = []
    for item in data:
        if item["active"]:
            name = item["name"]
            score = item["score"] * 1.5
            if score > 100:
                score = 100
            result.append({"name": name, "score": score})
    return result


def read_and_sum(filename):
    f = open(filename, "r")
    total = 0
    for line in f:
        val = int(line.strip())
        total = total + val
    return total


def get_user_status(user):
    if user:
        if user["age"] > 18:
            if user["vip"]:
                if user["vip_level"] == "gold":
                    return "gold_vip_adult"
                else:
                    if user["vip_level"] == "silver":
                        return "silver_vip_adult"
                    else:
                        return "normal_vip_adult"
            else:
                return "adult"
        else:
            if user["vip"]:
                return "vip_minor"
            else:
                return "minor"
    else:
        return "anonymous"
