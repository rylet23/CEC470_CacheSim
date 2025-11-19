import csv
from Cache_Level import Level

class AddressDecoder:
    def __init__(self, num_sets=1, block_size=1):
        self.num_sets = max(1, num_sets)
        self.block_size = max(1, block_size)

    def decode(self, address):
        block_addr = address // self.block_size
        index = block_addr% self.num_sets
        tag = block_addr //self.num_sets
        offset = address % self.block_size
        return tag, index, offset

class Heir:
    def __init__(self, l1_size=32, l2_size=128, l3_size=512, policy="LRU", block_size=1,
                 mapping_type="fully_associative", num_sets=None):
        # print("heir")
        self.policy = policy
        self.mapping_type = mapping_type

        self.l1 = Level("L1", l1_size, policy=self.policy, mapping_type=mapping_type, num_sets=num_sets)
        self.l2 = Level("L2", l2_size, policy=self.policy, mapping_type=mapping_type, num_sets=num_sets)
        self.l3 = Level("L3", l3_size, policy=self.policy, mapping_type=mapping_type, num_sets=num_sets)

        self.decoder = AddressDecoder(num_sets=1, block_size=block_size)

        self.l1_latency = 1
        self.l2_latency = 5
        self.l3_latency = 20
        self.mem_latency = 100

        self.total_accesses = 0
        self.main_memory_accesses = 0
        self.total_cycles = 0

    def _add_latency_for_path(self, path):
        if path == "L1":
            self.total_cycles += self.l1_latency
        elif path == "L2":
            self.total_cycles += (self.l1_latency + self.l2_latency)
        elif path == "L3":
            self.total_cycles += (self.l1_latency + self.l2_latency + self.l3_latency)
        elif path == "MEM":
            self.total_cycles += (self.l1_latency + self.l2_latency + self.l3_latency + self.mem_latency)

    def access(self, block_id):
        self.total_accesses += 1
        _tag, _index, _offset = self.decoder.decode(block_id)

        if self.l1.contains(block_id, touch=True):
            self.l1.record_hit()
            self._add_latency_for_path("L1")
            return "L1 hit"

        if self.l2.contains(block_id, touch=True):
            self.l2.record_hit()
            self.l2.remove(block_id)
            self._insert_with_pushdown(self.l1, block_id)
            self._add_latency_for_path("L2")
            return "L2 hit"

        if self.l3.contains(block_id, touch=True):
            self.l3.record_hit()
            self.l3.remove(block_id)
            self._insert_with_pushdown(self.l1, block_id)
            self._add_latency_for_path("L3")
            return "L3 hit"

        self.main_memory_accesses += 1
        self.l1.record_miss()
        self.l2.record_miss()
        self.l3.record_miss()
        self._insert_with_pushdown(self.l1, block_id)
        self._add_latency_for_path("MEM")
        return "Miss (main memory)"

    def _insert_with_pushdown(self, level, block_id):
        if level is self.l1:
            next_level = self.l2
        elif level is self.l2:
            next_level = self.l3
        else:
            next_level = None

        evicted = level.insert(block_id)
        if evicted is not None and next_level is not None:
            self._insert_with_pushdown(next_level, evicted)

    def _compute_amat(self):
        if self.total_accesses == 0:
            return 0.0
        return self.total_cycles / self.total_accesses

    def print_stats(self):
        print("\nCache Statistics:")
        for lvl in [self.l1, self.l2, self.l3]:
            s = lvl.stats()
            print(f"{s['name']}:")
            print(f"  Capacity: {s['capacity']}")
            print(f"  Policy: {s['policy']}")
            print(f"  Mapping: {s['mapping_type']}")
            print(f"  Sets: {s['num_sets']}, Ways/Set: {s['ways_per_set']}")
            print(f"  Accesses: {s['accesses']}")
            print(f"  Hits: {s['hits']}")
            print(f"  Misses: {s['misses']}")
            print(f"  Hit rate: {s['hit_rate'] * 100:.2f}%")
        print(f"\nMain memory accesses: {self.main_memory_accesses}")
        print(f"Total accesses: {self.total_accesses}")
        print(f"Total cycles: {self.total_cycles}")
        print(f"AMAT: {self._compute_amat():.2f}")

    def export_csv(self, filename="results.csv"):
        amat = self._compute_amat()
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["level", "capacity", "policy", "mapping_type", "num_sets", "ways_per_set",
                           "accesses", "hits", "misses", "hit_rate", "total_accesses_overall",
                           "main_memory_accesses", "total_cycles", "AMAT"])
            for lvl in [self.l1, self.l2, self.l3]:
                s = lvl.stats()

                writer.writerow([
                    s["name"],
                    s["capacity"],
                    s["policy"],
                    s["mapping_type"],
                    s["num_sets"],
                    s["ways_per_set"],
                    s["accesses"],
                    s["hits"],
                    s["misses"],
                    f"{s['hit_rate']:.4f}",
                    self.total_accesses,
                    self.main_memory_accesses,
                    self.total_cycles,
                    f"{amat:.4f}",
                ])
        print(f"Exported stats to {filename}")
