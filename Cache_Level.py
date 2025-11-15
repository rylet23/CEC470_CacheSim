import random

class Level:
    def __init__(self, name, capacity, policy="FIFO"):
        # print(capacity)

        self.name = name
        self.capacity = capacity
        self.policy = policy.upper() if policy else "FIFO"
        self.lines = []
        self.hits = 0
        self.misses = 0
        self._time_counter = 0

    def _touch_time(self):
        self._time_counter += 1
        return self._time_counter

    def contains(self, block_id, touch=False):
        for entry in self.lines:
            if entry["id"] == block_id:
                if touch:
                    entry["freq"] += 1
                    entry["last_used"] = self._touch_time()
                return True
        return False

    def remove(self, block_id):
        for i, entry in enumerate(self.lines):
            if entry["id"] == block_id:
                del self.lines[i]
                return True
            
            
        return False

    def _choose_victim_index(self):
        if not self.lines:
            return None

        if self.policy == "FIFO":
            return 0

        if self.policy == "RANDOM":
            return random.randint(0, len(self.lines) - 1)

        if self.policy == "LRU":
            min_idx = 0
            min_time = self.lines[0]["last_used"]
            for i, entry in enumerate(self.lines):
                if entry["last_used"] < min_time:
                    min_time = entry["last_used"]
                    min_idx = i
            return min_idx

        if self.policy == "LFU":
            min_idx = 0
            min_freq = self.lines[0]["freq"]
            min_time = self.lines[0]["last_used"]
            for i, entry in enumerate(self.lines):
                if entry["freq"] < min_freq:
                    min_freq = entry["freq"]
                    min_time = entry["last_used"]
                    min_idx = i
                elif entry["freq"] == min_freq and entry["last_used"] < min_time:
                    min_time = entry["last_used"]
                    min_idx = i
                    # print(min_idx)
            return min_idx

        return 0

    def insert(self, block_id):
        evicted_id = None
        if len(self.lines) >= self.capacity and self.capacity > 0:
            victim_index = self._choose_victim_index()
            if victim_index is not None:
                evicted_id = self.lines.pop(victim_index)["id"]

        entry = {"id": block_id, "freq": 1, "last_used": self._touch_time()}
        self.lines.append(entry)
        return evicted_id

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1

    def stats(self):
        accesses = self.hits + self.misses
        hit_rate = self.hits / accesses if accesses > 0 else 0.0
        # print(self.name)
        return {
        
            "name": self.name,
            "capacity": self.capacity,
            "policy": self.policy,
            # print(self.policy)
            "accesses": accesses,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
