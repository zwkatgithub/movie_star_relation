import os
import re
import requests
from bs4 import BeautifulSoup
from sql import db
from models import Movie, Star, Type, MovieType, Act


class Spider:
    base_url = "http://www.1905.com/"
    url = "http://www.1905.com/mdb/film/list/country-China/year-{}"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                       " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 "
                       "Safari/537.36")
    }
    num = re.compile(r'[0-9]+')
    page_format = "/o0d0p{page}.html"
    movie_image_path = os.path.join("images", "movies")
    star_image_path = os.path.join('images', "stars")
    movie_image_folder = os.path.join(
        os.path.dirname(__file__), movie_image_path)
    star_image_folder = os.path.join(
        os.path.dirname(__file__), star_image_path)
    star_dict = {
        "姓名": "name",
        "国家": "country",
        "身高": "height",
        "体重": "weight",
        "星座": "constellation",
        "出生日期": "birthday"
    }

    def _get_pages(self):
        soup = self._get_soup(self.url.format(self.year))
        content = soup.find(attrs={'class': 'lineG pl10 pb12'}).text
        pages = int(re.search(Spider.num, content))
        return pages

    def __init__(self, year, data_dict):
        self.year = year
        self.cur_url = Spider.url.format(self.year)
        self.pages = self._get_pages()
        self.data_dict = data_dict
        db.cursor.execute("SELECT id, content FROM type;")
        types = db.cursor.fetchall()
        self.type2id = {type_: idx for idx, type_ in types}

    def _crawling(self, url):
        soup = self._get_soup(url)
        div = soup.find(class_='leftArea')
        movies = div.find_all(name='li', class_='fl')
        assert len(movies) <= 30
        return movies

    def crawling(self):
        movies = self._crawling(self.cur_url)
        self.extract_info(movies)

    def download_img(self, img_url, filepath):
        img = requests.get(img_url, headers=Spider.headers)
        with open(filepath, 'wb') as file:
            file.write(img.content)

    def _get_movie_detail(self, movie):
        page = requests.get(
            Spider.base_url + movie.a['href'].text, headers=Spider.headers)
        soup = BeautifulSoup(page.text, 'lxml')
        return soup

    def _get_soup(self, url):
        page = requests.get(url, headers=Spider.headers)
        soup = BeautifulSoup(page.text, 'lxml')
        return soup

    def _create_movie(self, movie, movie_detail_soup):
        source_id = re.search(Spider.num, movie.a['href']).group()
        name = movie.a.img['alt']
        filename = movie.a.img['src'].split('/')[-1]
        img_path = os.path.join(Spider.movie_image_folder, filename)
        self.download_img(movie.a.img['src'], img_path)
        filepath = os.path.join(Spider.movie_image_path, filename)
        year = self.year
        score = movie.div.find('b').text
        introduction = movie_detail_soup.find('div', class_='plot').p.text
        ret = Movie(source_id, name, filepath, year, score, introduction)
        return ret

    def _insert_entity(self, entity):
        db.cursor.execute(entity.sql)
        db.cursor.execute("SELECT id FROM {} WHERE source_id=\'{}\';".format(
            entity.table_name, entity.source_id))
        return db.cursor.fetchone()[0]

    def _create_star(self, star_soup):
        star = Star(None, None, None, None, None, None, None, None, None)
        source_id = re.search(Spider.num, star_soup.a['href']).group()
        star_detail_soup = self._get_soup(
            Spider.base_url + star_soup.a['href'] + "details/")
        infos = star_detail_soup.find(
            'ul', class_="conts-top-list")
        infos = infos.find_all('li')
        for info in infos:
            key = info.span.text.replace('\xa0', '')
            if key in Spider.star_dict:
                value = info.em.text.replace('\xa0', '')
                setattr(star, Spider.star_dict[key], value)
        assert star.name is not None
        img_url = star_detail_soup.find('img', alt=star.name)['src']
        filepath = os.path.join(
            Spider.star_image_folder, img_url.split('/')[-1])
        self.download_img(img_url, filepath)
        star.image = os.path.join(
            Spider.star_image_path, img_url.split('/')[-1])
        star.source_id = source_id
        return star

    def _process_stars(self, movie_detail_url):
        star_soups, ids = self._get_star_soups(movie_detail_url)
        for star_soup in star_soups:
            star = self._create_star(star_soup)
            id_ = self._insert_entity(star)
            ids.append(id_)
        return ids

    def _get_star_soups(self, movie_detail_url):
        performers_url = movie_detail_url + 'performer/'
        soup = self._get_soup(performers_url)
        h3s = soup.find_all('h3')
        star_soups = None
        for h3 in h3s:
            if h3.text == '演员':
                star_soups = h3.find_next('div').find_all('div')
                break
        res = []
        ids = []
        if star_soups is not None:
            for star_soup in star_soups:
                source_id = re.search(Spider.num, star_soup.a['href']).group()
                db.cursor.execute(
                    "SELECT COUNT(*) FROM star WHERE source_id=\'{}\'".format(source_id))
                if db.cursor.fetchone()[0] == 0:
                    res.append(star_soup)
                else:
                    db.cursor.execute(
                        "SELECT id FROM star WHERE source_id=\'{}\';".format(source_id))
                    ids.append(db.cursor.fetchone()[0])

        return res, ids

    def _insert_movie_stars(self, movie_id, star_ids):
        for star_id in star_ids:
            act = Act(star_id, movie_id)
            db.cursor.execute(act.sql)

    def extract_info(self, movie_soups):
        for movie_soup in movie_soups:
            movie_detail_soup = self._get_soup(
                Spider.base_url + movie_soup.a['href'].text)
            movie = self._create_movie(movie_soup, movie_detail_soup)
            movie_id = self._insert_entity(movie)
            star_ids = self._process_stars(
                Spider.base_url + movie_soup.a['href'].text)
            self._insert_movie_stars(movie_id, star_ids)
            types = None
            for p in movie_soup.find_all("p"):
                if '类型' in p.text:
                    types = [pa.text for pa in p.find_all('a')]
            if types is not None:
                for type_ in types:
                    if self.type2id.get(type_, None) is None:
                        db.cursor.execute(
                            "INSERT INTO type VALUE (id, content=\'{}\');".format(type_))
                        db.cursor.execute(
                            "SELECT id FROM type WHERE content=\'{}\';".format(type_))
                        idx = db.cursor.fetchone()[0]
                        self.type2id.update({type_: idx})
                    idx = self.type2id[type_]
                    movietype = MovieType(movie_id, idx)
                    db.cursor.execute(movietype.sql)


if __name__ == "__main__":
    year = 2018
    spider = Spider(year, None)
    spider.crawling()