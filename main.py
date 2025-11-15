from heirarchy import Heir
from GenTrace import generate_trace, remove_trace
from gui import run_gui

def load_trace(filename):
    blocks = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                block_id = int(line, 16)
            except ValueError:
                continue
            blocks.append(block_id)
    return blocks

def run_cli():
    choice = input("Generate/modify trace file? (y = generate new, r = clear, n = use existing)\n").strip().lower()

    if choice == 'y':
        generate_trace()
    elif choice == 'r':
        remove_trace()
        print("Trace file cleared. Nothing to simulate yet.")
        return

    hierarchy = Heir(
        l1_size=32,
        l2_size=128,
        l3_size=512,
        policy="LRU",
        block_size=1
    )

    try:
        blocks = load_trace("TraceFile.txt")
    except FileNotFoundError:
        print("TraceFile.txt not found. Run again and generate a trace first.")
        return

    if not blocks:
        print("TraceFile.txt is empty. Generate a new trace and try again.")
        return

    for b in blocks:
        hierarchy.access(b)

    hierarchy.print_stats()
    hierarchy.export_csv("results.csv")

def main():
    mode = input("Launch GUI? (y = GUI, n = console)\n").strip().lower()
    if mode == "y":
        run_gui()
    else:
        run_cli()

if __name__ == "__main__":
    main()
