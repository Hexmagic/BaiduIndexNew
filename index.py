import requests
import json
import execjs
from datetime import datetime


class Baidu(object):
    def __init__(self):
        self.headers = {"Cookie": open("baidu.cookie").read()}
        self.decrypt = """
        function decrypt(t, e) {
            for (var a = t.split(""), i = e.split(""), n = {}, s = [], o = 0; o < a.length / 2; o++)
                n[a[o]] = a[a.length / 2 + o];
            for (var r = 0; r < e.length; r++)
                s.push(n[i[r]]);
            return s.join("")
        }
        """
        # js代码 懒得转换了，追求速度的可以自行转换
        self.cxt = execjs.compile(self.decrypt)

    def get(self, url: str):
        return requests.get(url, headers=self.headers)

    def build(self, keyword: str, start, end: str):
        url_plt = "http://index.baidu.com/api/SearchApi/index?area=0&word={}&startDate={}&endDate={}"
        if start:
            return url_plt.format(keyword, start, end)
        return "http://index.baidu.com/api/SearchApi/index?area=0&word={}&days=7".format(
            keyword
        )

    def search(self, keyword: str, start=None, end=str(datetime.now().date)):
        index_url = self.build(keyword, start, end)
        res = self.get(index_url)
        data = json.loads(res.content)
        indexs = data["data"]["userIndexes"][0]["all"]["data"]
        uid = data["data"]["uniqid"]
        ptbk_res = self.get(
            "http://index.baidu.com/Interface/api/ptbk?uniqid={}".format(uid)
        )
        ptbk = json.loads(ptbk_res.content)["data"]
        rst = self.cxt.call("decrypt", ptbk, indexs)
        return rst


def main():
    import sys
    word = sys.argv[1]
    arg_leng = len(sys.argv)
    bd = Baidu()
    if arg_leng == 2:
        print(bd.search(word))
    else:
        start = sys.argv[2]
        if len(sys.argv) == 4:
            end = sys.argv[3]
            print(bd.search(word, start, end))
        else:
            print(bd.search(word, start))

if __name__ == "__main__":
    main()
