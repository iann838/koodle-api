from datetime import datetime, timedelta
from collections import defaultdict

from bs4 import BeautifulSoup
import aiohttp

from ..utils.cache import SimpleCache
from .base import BaseScraper


class AmazonScraper(BaseScraper):

    NORMALIZED_CATEGORIES = {
        "all": "aps",
        "arts": "arts-crafts",
        "automotive": "automotive",
        "baby": "baby-products",
        "beauty": "beauty",
        "books": "stripbooks",
        "boys": "fashion-boys",
        "computers": "computers",
        "electronics": "electronics",
        "girls": "fashion-girls",
        "health": "hpc",
        "kitchen": "kitchen",
        "industrial": "industrial",
        "mens": "fashion-mens",
        "pets": "pets",
        "sports": "sporting",
        "games": "toys-and-games",
        "travel": "fashion-luggage",
        "womens": "fashion-womens",
    }
    BASE_URL = "https://www.amazon.com"
    CACHE = SimpleCache()

    cookies = defaultdict(str)
    last_updated = datetime.now()

    @classmethod
    async def search(cls, name: str, category: str):
        try:
            return cls.CACHE.get(f"{category}__{name}")
        except KeyError:
            pass
        url = f"/s?k={name.replace(' ', '+')}"
        url += f"&i={cls.NORMALIZED_CATEGORIES[category]}"
        url += "&ref=nb_sb_noss&url=search-alias%3Daps"
        async with aiohttp.ClientSession() as session:
            if datetime.now() - cls.last_updated >= timedelta(hours=2):
                cls.cookies.clear()
            r = await session.get(
                cls.BASE_URL + url,
                headers={
                    ":authority": "www.amazon.com",
                    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en",
                    "cache-control": "no-cache",
                    "ect": "4g",
                    "downlink": "9",
                    "pragma": "no-cache",
                    "rtt": "150",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "sec-ch-ua-mobile": '?0',
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": 'document',
                    "sec-fetch-mode": 'navigate',
                    "sec-fetch-site": 'none',
                    "sec-fetch-user": '?1',
                    "upgrade-insecure-requests": '1',
                    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                },
                cookies=cls.cookies
            )
            html = await r.text()

        results = []

        soup = BeautifulSoup(html, features="html.parser")
        # print(soup.prettify())
        featured_index = 0
        for search_item in soup.find_all(class_="s-result-item"):
            title_tag = search_item.find(name="h2")
            if not title_tag or not search_item.find(class_="a-price-whole"):
                continue
            o = {}
            o["title"] = title_tag.text.strip()
            try:
                o["link"] = title_tag.a["href"]
            except Exception:
                continue # Sponsored product broken link
            if o["link"].startswith("/"):
                o["link"] = "https://amazon.com" + o["link"]
            o["price"] = int(search_item.find(class_="a-price-whole").text.replace(".", "").replace(",", "")) + int(search_item.find(class_="a-price-fraction").text) / 100
            possible_rating = search_item.find(class_="a-row a-size-small")
            if possible_rating and "out of " in possible_rating.text:
                o["rating"] = float(possible_rating.text.split("out of")[0])
            else:
                o["rating"] = 0
            img_cont = search_item.find(attrs={"data-component-type": "s-product-image"})
            if img_cont:
                o["img"] = img_cont.find("img")['src']
            else:
                o["img"] = None
            o["store"] = "amazon"
            o["featured_index"] = featured_index
            o["id"] = cls.get_product_id(o["title"] or o["link"][:50])
            featured_index += 1
            results.append(o)

        if results:
            for cookie in session.cookie_jar:
                cls.cookies[cookie.key] = cookie.value
                print('Updated Amazon Cookie:', cookie.key, cookie.value)
            if not cls.cookies['session-token']:
                token_session_headers = {
                    ":authority": "www.amazon.com",
                    "accept": '*/*',
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en",
                    "content-type": "application/x-www-form-urlencoded",
                    "cache-control": "max-age=0",
                    "downlink": "3.55",
                    "ect": "4g",
                    "origin": "https://www.amazon.com",
                    "referer": "https://www.amazon.com/",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "sec-ch-ua-mobile": '?0',
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": 'empty',
                    "sec-fetch-mode": 'cors',
                    "sec-fetch-site": 'same-origin',
                    "sec-fetch-user": '?1',
                    "upgrade-insecure-requests": '1',
                    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                    "x-requested-with": "XMLHttpRequest",
                }
                async with aiohttp.ClientSession() as token_session:
                    r = await token_session.post(
                        cls.BASE_URL + "/gp/product/sessionCacheUpdateHandler.html",
                        headers=token_session_headers,
                        cookies=cls.cookies
                    )
                    html = await r.text()
                    # print(r)
                    for cookie in token_session.cookie_jar:
                        cls.cookies[cookie.key] = cookie.value
                        print('Updated Amazon Cookie:', cookie.key, cookie.value)
                    cls.last_updated = datetime.now()
                    r = await token_session.post(
                        cls.BASE_URL + "/gp/product/sessionCacheUpdateHandler.html",
                        headers=token_session_headers,
                        cookies=cls.cookies
                    )
                    html = await r.text()
                    # print(r)
                    for cookie in token_session.cookie_jar:
                        cls.cookies[cookie.key] = cookie.value
                        print('Updated Amazon Cookie:', cookie.key, cookie.value)
                    cls.last_updated = datetime.now()
        else:
            print("Amazon did not return any products")
        if len(results) >= 5:
            cls.CACHE.set(f"{category}__{name}", results)
        return results
