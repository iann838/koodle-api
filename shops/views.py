
import asyncio
from django.views import View
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from asgiref.sync import async_to_sync
import requests

from .scrapers.amazon import AmazonScraper
from .scrapers.alibaba import AlibabaScraper
from .scrapers.ebay import EbayScraper
from .constants import CATEGORIES


class CurrenciesView(View):

    def get(self, request: HttpRequest):
        # Register traffic here
        rates_req = requests.get("https://www.xe.com/api/protected/midmarket-converter/", headers={"Authorization": "Basic bG9kZXN0YXI6djdhOFdUZHZ3MTRmV2hRUEJMTEdiam5VYTNEWGN5RmM="})
        if rates_req.status_code != 200:
            rates_req = requests.get("http://www.convertmymoney.com/rates.json")
        if rates_req.status_code != 200:
            return JsonResponse({})
        return JsonResponse(rates_req.json()["rates"])


class SearchView(View):

    def get(self, request: HttpRequest, category: str, name: str):
        products = []
        if category not in CATEGORIES:
            return JsonResponse({"detail": "Category does not exist"}, status_code=404)
        # Register category here -
        product_lists = self.get_product_lists(name=name, category=category)
        for product_list in product_lists:
            products.extend(product_list)
        return JsonResponse(products, safe=False)

    @async_to_sync
    async def get_product_lists(self, name: str, category: str):
        results = []
        for _ in range(2):
            results = await asyncio.gather(
                AmazonScraper.search(name=name, category=category),
                AlibabaScraper.search(name=name, category=category),
                EbayScraper.search(name=name, category=category),
            )
            if sum([len(result) for result in results]):
                return results
        return results
