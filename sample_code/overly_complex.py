class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = []
        self.keys = []

    def get(self, key):
        for i in range(len(self.cache)):
            if self.cache[i][0] == key:
                value = self.cache[i][1]
                self.cache.pop(i)
                self.cache.append((key, value))
                return value
        return -1

    def put(self, key, value):
        for i in range(len(self.cache)):
            if self.cache[i][0] == key:
                self.cache.pop(i)
                break
        self.cache.append((key, value))
        if len(self.cache) > self.capacity:
            self.cache.pop(0)