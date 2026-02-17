from __future__ import annotations

from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@dataclass
class ScrapedReview:
    author: str
    text: str


@dataclass
class ScrapedMovie:
    title: str
    year: int | None
    overview: str
    reviews: list[ScrapedReview]
    page_url: str


class ScraperClient:
    def __init__(self, selenium_url: str, base_url: str) -> None:
        self._selenium_url = selenium_url
        self._base_url = base_url

    def search(self, limit: int = 15):
        driver = None
        try:
            driver = webdriver.Remote(command_executor=self._selenium_url, options=Options())
            driver.get(self._base_url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            movie_list = self._get_movie_list(soup, limit)
            results = []
            for (title, href) in movie_list:
                movie = self._parse_movie(driver, title, href)
                results.append(movie)
            return results
        finally:
            if driver is not None:
                driver.quit()


    def _get_movie_list(self, soup, limit):
        section_header = soup.find("h2", string=lambda t: t and "Зарубежные фильмы" in t)
        movies = []

        for el in section_header.find_all_next():
            if el.name == "h2":
                break
            classes = el.get("class", [])
            if el.name == "tr" and ("tum" in classes or "gai" in classes):
                link = el.find("a", href=lambda h: h and h.startswith("/torrent/"))
                if link:
                    movies.append((link.text, link["href"]))
            if len(movies) >= limit:
                break
        return movies

    def _parse_movie(self, driver, title, url):
        full_url = urljoin(self._base_url, url)
        driver.get(full_url)
        html = driver.page_source
        soup2 = BeautifulSoup(html, "html.parser")
        marker = soup2.find("b", string=lambda t: t and "О фильме" in t)
        overview = ""
        if marker and marker.next_sibling:
            overview = marker.next_sibling.get_text(strip=True)
        reviews = self._parse_reviews(soup2)

        return ScrapedMovie(
            title=title,
            year=None,
            overview=overview,
            reviews=reviews,
            page_url=full_url,
        )

    def _parse_reviews(self, soup):
        return []

