from bs4 import BeautifulSoup
import aiohttp
import asyncio

from ..utils.cache import SimpleCache
from .base import BaseScraper


class EbayScraper(BaseScraper):

    NORMALIZED_CATEGORIES = {
        "all": "0",
        "arts": "550",
        "automotive": "6000",
        "baby": "2984",
        "beauty": "26395",
        "books": "267",
        "boys": "260013",
        "computers": "58058",
        "electronics": "293",
        "girls": "260015",
        "health": "26395",
        "kitchen": "20625",
        "industrial": "12576",
        "mens": "1059",
        "pets": "1281",
        "sports": "888",
        "games": "233",
        "travel": "3252",
        "womens": "15724",
    }
    BASE_URL = "https://www.ebay.com"
    CACHE = SimpleCache()

    @classmethod
    async def search(cls, name: str, category: str):
        try:
            return cls.CACHE.get(f"{category}__{name}")
        except KeyError:
            pass
        url = cls.BASE_URL + f"/sch/i.html?_from=R40&_nkw={name}&_sacat={cls.NORMALIZED_CATEGORIES[category]}&_fcid=1"
        headers = {
            ":authority": "www.ebay.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en",
            "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        }

        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                r = await session.get(url, headers=headers)
                html = await r.text()
            except asyncio.exceptions.TimeoutError:
                print("Ebay did not return any products")
                return []

        soup = BeautifulSoup(html, 'html.parser')
        product_data= soup.findAll('div', attrs={'class': 's-item__wrapper clearfix'})

        product_list = []

        for featured_index, each_product in enumerate(product_data):
            price = (each_product.findNext('span', attrs={'class': 's-item__price'}).text or "").replace("$", "").replace("USD", "").replace(",", "").replace(u"\xa0", "")
            if "price" in price.lower() or "precio" in price.lower():
                price = None
            price_range = None
            if price is None:
                pass
            elif " to " in price:
                price_range = [float(pric) for pric in price.split(" to ")]
            elif " a " in price:
                price_range = [float(pric) for pric in price.split(" a ")]
            product = {
                'title': each_product.findNext('h3', attrs={'class': 's-item__title'}).text,
                'price': None,
                'price_range': None,
                'link': each_product.findNext('a', attrs={'class': 's-item__link'})['href'],
                'img': each_product.findNext('img', attrs={'class': 's-item__image-img'})['src'],
                'rating': 0,
                "featured_index": featured_index,
                "store": "ebay"
            }
            product["id"] = cls.get_product_id(product["title"] or product["link"][:50])
            if price_range:
                product['price_range'] = price_range
                product['price'] = price_range[0]
            elif price:
                try:
                    product['price'] = float(price)
                except ValueError:
                    pass
            if each_product.findNext('span', attrs={'class': 'clipped'}) is not None:
                star_text: str = each_product.findNext('span', attrs={'class': 'clipped'}).text
                if "stars" in star_text:
                    product['rating'] = float(star_text.split(" out of ")[0])
                elif "estrellas" in star_text:
                    product['rating'] = float(star_text.split(" de ")[0])

            if product["title"]:
                product_list.append(product)

        if not product_list:
            print("Ebay did not return any products")
        if len(product_list) >= 5:
            cls.CACHE.set(name, product_list)
        return product_list
