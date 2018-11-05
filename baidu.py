import requests
import json
import execjs

class Baidu(object):
    def __init__(self):
        self.headers = {
            'Cookie':'BIDUPSID=9E709826BD0229A18D94190D2ACFA223; PSTM=1540976696; BAIDUID=21C4BB6D41623D5D202078CCDEEB3773:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDUSS=h-QUdYYU5pRnlpMnAyVVIySVpEbWt1ZlRzVlBKVmlJcVFNZEtwcDE0SXVvQWRjQVFBQUFBJCQAAAAAAAAAAAEAAAAGLdBOS2FsaUJhY2tCb3gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4T4FsuE-BbMX; bdindexid=ejmh4lnh4bgshvh7thmvptupb2; CHKFORREG=ad837793fce4d36c9dfa438664c82daa; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1540976230,1540980112,1541411530,1541414555; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1541414555'
        }
        self.decrypt = '''
        function decrypt(t, e) {
            for (var a = t.split(""), i = e.split(""), n = {}, s = [], o = 0; o < a.length / 2; o++)
                n[a[o]] = a[a.length / 2 + o];
            for (var r = 0; r < e.length; r++)
                s.push(n[i[r]]);
            return s.join("")
        }
        '''
        self.cxt = execjs.compile(self.decrypt)
    
    def get(self, url):
        return requests.get(url,headers=self.headers)
    def search(self, keyword):
        index_area = 'http://index.baidu.com/api/SearchApi/index?area=0&word=eth&days=7'
        res = self.get(index_area)
        data = json.loads(res.content)
        indexs = data['data']['userIndexes'][0]['all']['data']
        uniqid = data['data']['uniqid']
        ptbk_res = self.get('http://index.baidu.com/Interface/api/ptbk?uniqid={}'.format(uniqid))
        ptbk = json.loads(ptbk_res.content)['data']
        rst = self.cxt.call("decrypt", ptbk, indexs)
        print(rst)

def main():
    bd = Baidu()
    bd.search("btc")
if __name__ == '__main__':
    main()
    