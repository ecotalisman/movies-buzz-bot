from __future__ import annotations

import re

from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin


SECTION_FOREIGN = "Зарубежные фильмы"
MOVIE_INFO_MARKERS = ["О фильме", "Описание"]
MOVIE_INFO_TAGS = "b"


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
            for (title, href, year) in movie_list:
                movie = self._parse_movie(driver, title, href, year)
                results.append(movie)
            return results
        finally:
            if driver is not None:
                driver.quit()


    def _get_movie_list(self, soup, limit):
        section_header = None

        for h2 in soup.find_all("h2"):
            full_text = h2.get_text(strip=True)
            if SECTION_FOREIGN in full_text:
                section_header = h2
                break

        if section_header is None:
            return []

        movies = []

        for el in section_header.find_all_next():
            if el.name == "h2":
                break
            classes = el.get("class", [])
            if el.name == "tr" and ("tum" in classes or "gai" in classes):
                link = el.find("a", href=lambda h: h and h.startswith("/torrent/"))
                if link:
                    raw_title = link.text
                    match = re.search(r'\((\d{4})\)', raw_title)
                    if match:
                        clean_title = raw_title[:match.end()].strip()
                        year = int(match.group(1))
                    else:
                        clean_title = raw_title.strip()
                        year = None
                    movies.append((clean_title, link["href"], year))
            if len(movies) >= limit:
                break
        return movies

    def _parse_movie(self, driver, title, url, year):
        full_url = urljoin(self._base_url, url)
        driver.get(full_url)
        html = driver.page_source
        soup2 = BeautifulSoup(html, "html.parser")
        marker = None

        for b_tag in soup2.find_all(MOVIE_INFO_TAGS):
            b_text = b_tag.get_text(strip=True)
            if any(m in b_text for m in MOVIE_INFO_MARKERS):
                marker = b_tag
                break

        overview = ""
        if marker:
            for sibling in marker.next_siblings:
                text = sibling.get_text() if hasattr(sibling, "get_text") else str(sibling)
                clean = text.replace('\xa0', ' ').strip(': \t\n\r')
                if clean:
                    overview = clean
                    break

        reviews = self._parse_reviews(soup2)

        return ScrapedMovie(
            title=title,
            year=year,
            overview=overview,
            reviews=reviews,
            page_url=full_url,
        )

    def _parse_reviews(self, soup):
        return []
