import asyncio
from bs4 import BeautifulSoup
import aiohttp

from .base import BaseScraper


class AlibabaScraper(BaseScraper):

    BASE_URL = "https://www.alibaba.com"

    @classmethod
    async def search(cls, name: str, category: str):
        url = cls.BASE_URL + "/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=" + name
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }

        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                r = await session.get(url, headers=headers)
                html = await r.text()
            except asyncio.exceptions.TimeoutError:
                print("Alibaba did not return any products")
                return []

        soup = BeautifulSoup(html, 'html.parser')
        product_data = soup.findAll('div', attrs={'class': 'list-no-v2-inner m-gallery-product-item-v2 img-switcher-parent'}) 

        product_list = []

        for featured_index, each_product in enumerate(product_data):
            price_el = each_product.find('span', attrs={'class': 'elements-offer-price-normal__price'})
            if not price_el:
                continue
            price = (price_el.text or "").replace("$", "").replace(",", "")
            price_range = None
            if "-" in price:
                price_range = [float(pric) for pric in price.split("-")]
            product = {
                'title': each_product.find('p', attrs={'class': 'elements-title-normal__content large'}).text,
                'price': None,
                'price_range': None,
                'link': 'https://' + each_product.find('a', attrs={'class': 'elements-title-normal one-line'})['href'].lstrip("/"), 
                'img':'https://' + each_product.find('div', attrs={'class': 'seb-img-switcher__imgs'})['data-image'].lstrip("/"),
                'rating': 0,
                "featured_index": featured_index,
                "store": "alibaba"
            }
            product["id"] = cls.get_product_id(product["title"] or product["link"][:50])
            if price_range:
                product['price_range'] = price_range
                product['price'] = price_range[0]
            else:
                try:
                    product['price'] = float(price)
                except ValueError:
                    pass
            product_list.append(product)
        
        if not product_list:
            print("Alibaba did not return any products")
        return product_list
