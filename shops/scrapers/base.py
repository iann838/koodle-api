from abc import ABC, abstractclassmethod
from typing import Dict, List
import base64


class BaseScraper(ABC):

    @classmethod
    def get_product_id(cls, name: str):
        return base64.b64encode(name.encode()).rstrip(b"=").decode('ascii')

    @abstractclassmethod
    def search(cls, name: str, category: str) -> List[Dict]:
        pass
