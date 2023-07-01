import datetime
import functools
import hashlib
from importlib.util import source_hash
import json
from os import times
import re
from tracemalloc import start
from bs4 import BeautifulSoup
import requests
from sqlalchemy import func, select, text
import tqdm
from db.engine import get_engine, get_session
from db.models import SourceHTML, Movie, Category, CategoryMovie
from db.models.movielink import MovieLink


def run():
    # 获取所有未处理的source html
    with get_session() as session:
        statement = (
            select(SourceHTML)
            # .where(SourceHTML.source_hash.not_in(select(Movie.source_hash)))
            .order_by(SourceHTML.id.asc())
        )
        unhandled_source_htmls = list(session.scalars(statement).all())

    all_links = []

    for unhandled_source_html in tqdm.tqdm(unhandled_source_htmls):
        # print(unhandled_source_html.source)
        html = BeautifulSoup(unhandled_source_html.content, "html.parser")
        html_details_container = html.find("div", class_="main").find(
            "div", class_="m-details"
        )

        name = (
            html_details_container.find("div", class_="info")
            .find("span", string=re.compile(r"片名：.+$"))
            .text.strip("片名：")
            .strip()
        )

        # print(name)
        # print(html_details_container.find("div", class_="txt"))
        tag_txt_p_list = html_details_container.select(".txt > p")
        # print(tag_txt_p_list)
        if len(tag_txt_p_list) <= 1:
            tag_txt_p_list = html_details_container.select(".txt > img > p")

        txt_infos = []
        txt_info = []
        for tag_txt_p in tag_txt_p_list:
            if len(tag_txt_p.find_all("img")):
                txt_infos.append(txt_info)
                txt_info = []
                continue

            if tag_txt_p.text.strip().startswith("◎"):
                txt_infos.append(txt_info)
                txt_info = [tag_txt_p.text]
                continue

            txt_info.append(tag_txt_p.text)

        txt_infos = [
            [re.sub(r"\s+", " ", j.strip()) for j in i if j.strip() != ""]
            for i in txt_infos
            if len(i) > 0 and i[0].startswith("◎")
        ]

        txt_infos = {
            re.match(r"^◎((.\s+.)|([^ ]+))", txt_info[0]).groups()[0]: txt_info
            for txt_info in txt_infos
        }
        # print(txt_infos)

        txt_infos = {
            re.sub(r"\s+", "", name): [
                i.strip()
                for i in [
                    txt_info[0].lstrip("◎").lstrip(name).strip(),
                    *txt_info[1:],
                ]
                if i.strip() != ""
            ]
            for name, txt_info in txt_infos.items()
        }

        txt_infos = {
            name: [
                *(
                    [txt_info[0]]
                    if txt_info[0].startswith("http://")
                    or txt_info[0].startswith("https://")
                    or "评分" in name
                    else [i.strip() for i in txt_info[0].split("/")]
                ),
                *txt_info[1:],
            ]
            for name, txt_info in txt_infos.items()
            if len(txt_info) > 0
        }
        # print(txt_infos)

        other_names = [*txt_infos.get("片名", []), *txt_infos.get("译名", [])]
        # print("other_names:", other_names)

        release_year = int(txt_infos["年代"][0])
        # print("release_year:", release_year)

        release_date = txt_infos.get("上映日期", [])
        # print("release_date:", release_date)

        production_country = txt_infos.get("产地", [])
        # print("production_country:", production_country)

        language = "" if len(txt_infos.get("语言", [])) == 0 else txt_infos["语言"][0]
        # print("language:", language)

        languages = txt_infos.get("语言", [])[1:]
        # print("languages:", languages)

        covers = [i["src"] for i in html_details_container.select(".txt > img")]
        # print("covers:", covers)

        description = "" if len(txt_infos.get("简介", [])) == 0 else txt_infos["简介"][0]
        # print("description:", description)

        # print("video length:", txt_infos.get("片长", txt_infos.get("单集片长")))
        video_length = [
            int(re.match(r"^(.*?)(\d+)\s*分钟.*$", i.strip()).groups()[1]) * 60
            for i in txt_infos.get("片长", txt_infos.get("单集片长", []))
            if re.match(r"^(.*?)(\d+)\s*分钟.*$", i.strip()) is not None
        ]

        # if len(video_length) == 0:
        #     print(
        #         "video_length={}, source={}".format(
        #             video_length, unhandled_source_html.source
        #         )
        #     )
        video_length = video_length[0] if len(video_length) > 0 else 0
        # print("video length:", video_length)

        categories = txt_infos.get("类别", [])
        # print("categories:", categories)

        links = [
            tag_a["href"]
            for tag_a in html_details_container.find("div", class_="bot").select("p a")
            if tag_a["href"] != ""
        ]
        all_links.extend(links)

        with get_session() as session:
            saved_categories = list(
                session.scalars(
                    select(Category).where(Category.name.in_(categories))
                ).all()
            )
            unsaved_categories = [i for i in categories if i not in saved_categories]
            if len(unsaved_categories) > 0:
                unsaved_categories = [Category(name=i) for i in unsaved_categories]
                session.add_all(unsaved_categories)

            movie_id = session.scalar(
                select(Movie.id).where(
                    Movie.source_hash == unhandled_source_html.source_hash
                )
            )
            if movie_id is None:
                movie = Movie(
                    name=name,
                    other_names=json.dumps(other_names, ensure_ascii=False),
                    source=unhandled_source_html.source,
                    source_hash=unhandled_source_html.source_hash,
                    release_year=release_year,
                    release_date=json.dumps(release_date, ensure_ascii=False),
                    production_country=json.dumps(
                        production_country, ensure_ascii=False
                    ),
                    language=language,
                    languages=json.dumps(languages, ensure_ascii=False),
                    cover=json.dumps(covers, ensure_ascii=False),
                    description=description,
                    video_length=video_length,
                )
                session.add(movie)
                session.flush()
                movie_id = movie.id

            saved_movie_categories = list(
                session.scalars(
                    select(CategoryMovie).where(CategoryMovie.movie_id == movie_id)
                ).all()
            )
            unsaved_movie_categories = [
                i for i in categories if i not in saved_movie_categories
            ]
            if len(unsaved_movie_categories) > 0:
                unsaved_movie_categories = [
                    CategoryMovie(category_name=i, movie_id=movie_id)
                    for i in unsaved_movie_categories
                ]
                session.add_all(unsaved_movie_categories)

            saved_movie_links = list(
                set(
                    session.scalars(
                        select(MovieLink).where(MovieLink.movie_id == movie_id)
                    ).all()
                )
            )
            unsaved_movie_links = [i for i in links if i not in saved_movie_links]
            if len(unsaved_movie_links) > 0:
                unsaved_movie_links = [
                    MovieLink(movie_id=movie_id, link=i) for i in unsaved_movie_links
                ]
                session.add_all(unsaved_movie_links)

            session.commit()

    # print([link for link in all_links if not link.startswith("magnet:")])


def test():
    from sqlalchemy import text

    with get_session() as session:
        print(
            session.execute(
                select(CategoryMovie.category_name, func.count(text("*")))
                .group_by(CategoryMovie.category_name)
            ).all()
            # list(
            #     session.scalars(
            #         text(
            #             "select category_name, count(*) from category_movie group by category_name"
            #         )
            #     ).all()
            # )
        )


if __name__ == "__main__":
    # run()
    test()
