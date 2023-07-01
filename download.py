import datetime
import functools
import hashlib
from importlib.util import source_hash
from os import times
import re
from tracemalloc import start
from bs4 import BeautifulSoup
import requests
from sqlalchemy import select, text
import tqdm
from db.engine import get_engine, get_session
from db.models import SourceHTML, movie

DOMAIN = "https://www.bt-tt.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
COMMON_HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": "https://www.bt-tt.com/html/3-0.html",
    "Sec-Ch-Ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
}


# def download_movie_default():
#     resp = requests.get(
#         "https://www.bt-tt.com/html/1/31857.html", headers=COMMON_HEADERS
#     )
#     resp.raise_for_status()
#     html = BeautifulSoup(resp.content.decode(), "html.parser")
#     container = list(html.body.find_all("div", class_="container")[0])

#     print(container)


def print_datetime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        try:
            response = func(*args, **kwargs)
            return response
        except:
            raise
        finally:
            end_time = datetime.datetime.now()
            print(
                "start_time: {}, end_time: {}, timedelta: {}".format(
                    start_time, end_time, end_time - start_time
                )
            )

    return wrapper


# 延时发送请求
def delay(seconds=1):
    import datetime
    import time

    def wrapper(func):
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=seconds + 1)

        @functools.wraps(func)
        def wrapper_(*args, **kwargs):
            # 返回的是最里面的这个wrapper_因为start_time不是local的不改变它永远都不会变
            nonlocal start_time
            try:
                ret = func(*args, **kwargs)
                return ret
            except:
                raise
            finally:
                end_time = datetime.datetime.now()
                time_elapsed = (end_time - start_time).total_seconds()
                if time_elapsed < seconds:
                    time.sleep(seconds - time_elapsed)
                start_time = datetime.datetime.now()

        return wrapper_

    return wrapper



# 遇到打不开的数据重试times次
def retry(times=3):
    def wrapper(func):
        @functools.wraps(func)
        def wrapper_(*args, **kwargs):
            # 返回的是最里面的这个wrapper_因为start_time不是local的不改变它永远都不会变
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except KeyboardInterrupt:
                    raise
                except:
                    if i >= times - 1:
                        raise

        return wrapper_

    return wrapper


# @print_datetime
@retry(times=3)
@delay(seconds=1)
def send_get_requests(url, *args, **kwargs):
    kwargs["headers"] = dict(COMMON_HEADERS, **kwargs.get("headers", {}))
    response = requests.get(url, *args, **kwargs)
    response.raise_for_status()
    return response


def crawl_movies_by_category():
    # category_ids = [i for i in range(1, 14)]
    category_ids = [1]

    for category_id in category_ids:
        resp = send_get_requests(
            "https://www.bt-tt.com/html/{}-0.html".format(category_id),
            headers=COMMON_HEADERS,
        )
        html = BeautifulSoup(resp.content.decode(), "html.parser")
        website_category_name = (
            html.find("div", class_="main")
            .find("div", class_="m-film")
            .find("div", class_="cur")
            .find("a", href=re.compile(r"/html/\d+-0\.html$"))
            .text.strip()
        )

        total_pages = [
            i["href"]
            for i in html.find("div", class_="pages").find_all(
                "a", href=re.compile(r"^/html/\d+-\d+\.html$")
            )
            if i.text.strip() == "尾页"
        ][0]

        total_pages = (
            int(re.match(r"^/html/\d+-(\d+)\.html$", total_pages).groups()[0]) + 1
        )
        # print(total_pages)

        for page_no in range(0, total_pages):
            resp = send_get_requests(
                "https://www.bt-tt.com/html/{}-{}.html".format(category_id, page_no),
                headers=COMMON_HEADERS,
            )
            html = BeautifulSoup(resp.content.decode(), "html.parser")

            movie_default_urls = list(
                set(
                    [
                        DOMAIN + i["href"]
                        for i in html.find("div", class_="main").find_all(
                            "a", href=re.compile(r"^/html/\d+/\d+\.html$")
                        )
                    ]
                )
            )

            # print(movie_default_urls, len(movie_default_urls))

            for movie_default_url in tqdm.tqdm(
                movie_default_urls,
                desc="category={}, page={}".format(website_category_name, page_no + 1),
            ):
                resp = send_get_requests(movie_default_url, headers=COMMON_HEADERS)

                movie_default_url_hash = hashlib.md5(
                    movie_default_url.encode("utf-8")
                ).hexdigest()

                with get_session() as session:
                    if (
                        session.scalars(
                            select(SourceHTML).where(
                                SourceHTML.source_hash == movie_default_url_hash
                            )
                        ).first()
                        is not None
                    ):
                        continue

                with get_session() as session:
                    session.add(
                        SourceHTML(
                            source=movie_default_url,
                            source_hash=movie_default_url_hash,
                            content=resp.content.decode(),
                        )
                    )
                    session.commit()


def run():
    # engine = get_engine()
    # # with engine.connect() as conn:
    # #     print([i for i in conn.scalars(text("show databases")).all()])
    # with get_session() as session:
    #     print([i for i in session.scalars(text("show databases")).all()])
    # print(download_movie_default())
    crawl_movies_by_category()


if __name__ == "__main__":
    run()
