from datetime import datetime, timedelta
from typing import TypeVar, Generic, Optional, Type


T = TypeVar("T")


class SimpleCache(Generic[T]):
    '''
    A high performance mini local cache.
    This cache will not copy the objects on get/put, modification to objects affects cached objects.
    You can pass a class to instantiation param `class_of_t` for typing and autocompletion if all your objects are the same type.
    '''
    objects: dict
    max_entries: int

    def __init__(self, expiration=60, max_entries=5000, class_of_t: Optional[Type[T]] = None):
        self.objects = {}
        self.expiration = expiration
        self.max_entries = max_entries

    def get(self, name: str) -> T:
        '''
        Get an object from the cache.
        '''
        data = self.objects[name]
        if data[1] is not None and data[1] < datetime.now():
            del self.objects[name]
            raise KeyError(name)
        return data[0]

    def set(self, name: str, val: T, exp: int = None):
        '''Put an object to the cache.'''
        if exp is None:
            exp = self.expiration
        if exp >= 0:
            self.objects[name] = [val, datetime.now() + timedelta(seconds=exp)]
        else:
            self.objects[name] = [val, None]
        if len(self.objects) > self.max_entries:
            number = 0
            for key in self.objects:
                if number < self.max_entries / 2:
                    del self.objects[key]
                    number += 1
                    continue
                break
        return name

    def clear(self):
        '''Clear the cache.'''
        self.objects = dict()
