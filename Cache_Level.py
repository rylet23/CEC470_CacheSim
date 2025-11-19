import random

class Level:
    def __init__(self, name, capacity, policy="FIFO", mapping_type="fully_associative", num_sets=None):
        # print(capacity)

        self.name = name
        self.capacity = capacity
        self.policy = policy.upper() if policy else "FIFO"
        self.mapping_type = mapping_type.lower()

        # Determine number of sets and ways based on mapping type
        if self.mapping_type == "direct_mapped":
            self.num_sets = capacity
            self.ways_per_set = 1
        elif self.mapping_type == "fully_associative":
            self.num_sets = 1
            self.ways_per_set = capacity
        elif self.mapping_type == "set_associative":
            if num_sets is None or num_sets <= 0:
                # Default to 2-way set associative
                self.num_sets = max(1, capacity // 2)
            else:
                self.num_sets = min(num_sets, capacity)
            self.ways_per_set = max(1, capacity // self.num_sets)
        else:
            # Default to fully associative
            self.num_sets = 1
            self.ways_per_set = capacity

        # Storage: dictionary of sets, each set contains a list of cache lines
        self.sets = {i: [] for i in range(self.num_sets)}

        self.hits = 0
        self.misses = 0
        self._time_counter = 0

    def _touch_time(self):
        self._time_counter += 1
        return self._time_counter

    def _get_set_index(self, block_id):
        """Calculate which set this block belongs to"""
        return block_id % self.num_sets

    def contains(self, block_id, touch=False):
        set_index = self._get_set_index(block_id)
        for entry in self.sets[set_index]:
            if entry["id"] == block_id:
                if touch:
                    entry["freq"] += 1
                    entry["last_used"] = self._touch_time()
                return True
        return False

    def remove(self, block_id):
        set_index = self._get_set_index(block_id)
        for i, entry in enumerate(self.sets[set_index]):
            if entry["id"] == block_id:
                del self.sets[set_index][i]
                return True


        return False

    def _choose_victim_index(self, cache_set):
        if not cache_set:
            return None

        if self.policy == "FIFO":
            return 0

        if self.policy == "RANDOM":
            return random.randint(0, len(cache_set) - 1)

        if self.policy == "LRU":
            min_idx = 0
            min_time = cache_set[0]["last_used"]
            for i, entry in enumerate(cache_set):
                if entry["last_used"] < min_time:
                    min_time = entry["last_used"]
                    min_idx = i
            return min_idx

        if self.policy == "LFU":
            min_idx = 0
            min_freq = cache_set[0]["freq"]
            min_time = cache_set[0]["last_used"]
            for i, entry in enumerate(cache_set):
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
        set_index = self._get_set_index(block_id)
        cache_set = self.sets[set_index]

        # Check if this specific set is full
        if len(cache_set) >= self.ways_per_set and self.ways_per_set > 0:
            victim_index = self._choose_victim_index(cache_set)
            if victim_index is not None:
                evicted_id = cache_set.pop(victim_index)["id"]

        entry = {"id": block_id, "freq": 1, "last_used": self._touch_time()}
        cache_set.append(entry)
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
            "mapping_type": self.mapping_type,
            "num_sets": self.num_sets,
            "ways_per_set": self.ways_per_set,
            # print(self.policy)
            "accesses": accesses,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
