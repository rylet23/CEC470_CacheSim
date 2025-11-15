import random
def generate_trace(filename = "TraceFile.txt", n=10000):
    with open(filename, "w") as f:
        for _ in range(n):
            addr = random.randint(0, 0xFF)
            f.write(f"{addr:02X}\n")
def remove_trace(filename = "TraceFile.txt"):
    with open(filename, "w") as f:
        pass
            
            
    