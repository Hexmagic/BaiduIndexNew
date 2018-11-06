import click
from baidu.baidu import BaiduIndex
from util import load_file_to_dic
import asyncio

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
