import aiohttp
import asyncio
from util import dump_dic, to_dic, load_file_to_dic
import execjs
from logzero import logger
from datetime import datetime, timedelta
from dateutil import parser
import click
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
            self.cookies.append(pa.read_text())

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
        pass


@click.command()
@click.option("-k", default=None, help="搜索词列表，以,分割")
@click.option("-s", default=None, help="自定义搜索开始的日期")
@click.option("-e", default=None, help="自定义搜索结束的日期")
@click.option("-f", default=None, help="搜索词文件")
@click.option(
    "-d", default=None, help="搜索日期间隔(不传递开始日期的时候默认倒退d天到现在的期间),不传递的话默认只运行一次,可以传递数字例如30"
)
@click.option("-r", default=10, help="搜索间隔，搜索的太快会被封号")
def main(k, s, e, d, f, r):
    bd = BaiduIndex(r)
    if k:
        words = k.split(",")
        bd.bootstrap(words)
    elif f:
        bd.bootstrap(f >> load_file_to_dic)
    else:
        print("输入 python app.py --help 查看帮助")
    coro = bd.run(s, e, d)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(coro))


if __name__ == "__main__":
    main()
