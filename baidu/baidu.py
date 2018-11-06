import aiohttp
import asyncio
from util import dump_dic, to_dic
import execjs
from logzero import logger
from datetime import datetime, timedelta
from dateutil import parser
import pathlib
import random


class BaiduIndex(object):
    def __init__(self, r):
        self.delay = r
        self.session = None
        self.keywords = []
        self.cookies = []
        self.decrypt = """
        function decrypt(t, e) {
            for (var a = t.split(""), i = e.split(""), n = {}, s = [], o = 0; o < a.length / 2; o++)
                n[a[o]] = a[a.length / 2 + o];
            for (var r = 0; r < e.length; r++)
                s.push(n[i[r]]);
            return s.join("")
        }
        """
        self.cxt = execjs.compile(self.decrypt)

    async def sleep(self, delay):
        await asyncio.sleep(delay)

    async def get(self, url, binary=False, proxy=None):
        headers = {
            "Cookie": random.choice(self.cookies),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36",
        }
        async with self.session.get(url, proxy=proxy, headers=headers) as res:
            if binary:
                content = await res.read()
            else:
                content = await res.text()
            return content

    def bootstrap(self, keywords):
        self.keywords = keywords
        for pa in pathlib.Path("cookie").iterdir():
            cookie_text = pa.read_text()
            if cookie_text:
                self.cookies.append(cookie_text)
        if not self.cookies:
            logger.error("没有可用cookie")
            exit(0)

    def build(self, keyword: str, start, end: str):
        url_plt = "http://index.baidu.com/api/SearchApi/index?area=0&word={}&startDate={}&endDate={}"
        if start:
            return url_plt.format(keyword, start, end)
        return "http://index.baidu.com/api/SearchApi/index?area=0&word={}&days=7".format(
            keyword
        )

    async def run(self, start=None, end=None, duration=None):
        self.session = aiohttp.ClientSession()
        start_time = datetime.now()
        while True:
            if start and end:
                pass
            elif end and duration:
                end_date = parser.parse(end)
                start_date = end_date - timedelta(days=duration)
                start = str(start_date)
            elif start and duration:
                start_date = parser.parse(start)
                end_date = start_date + timedelta(days=duration)
                end = str(end_date)
            await self._run(start, end)
            if not duration:
                break
            tomorrow_time = start_time + timedelta(days=1)
            sleep_seconds = tomorrow_time - start_time
            await self.sleep(sleep_seconds.total_seconds())
            start_time = tomorrow_time
        await self.session.close()
        return "Done"

    async def _run(self, start: str, end: str):
        leng = len(self.keywords)
        for ix, keyword in enumerate(self.keywords):
            await self.search(keyword, start, end)
            if ix != leng - 1:
                await self.sleep(self.delay)

    async def search(self, keyword, start, end):
        url = self.build(keyword, start, end)
        data = await self.get(url) >> to_dic
        indexs = data["data"]["userIndexes"][0]["all"]["data"]
        uid = data["data"]["uniqid"]
        ptbk = (
            await self.get(
                "http://index.baidu.com/Interface/api/ptbk?uniqid={}".format(uid)
            )
            >> to_dic
        )["data"]
        string = self.cxt.call("decrypt", ptbk, indexs)
        rst = {"keyword": keyword, "lst": string.split(",")}
        logger.info(rst)
        await self.save(keyword, rst, start, end)

    async def save(self, keyword, rst, start, end):
        # 此处自定义存储位置
        pass


