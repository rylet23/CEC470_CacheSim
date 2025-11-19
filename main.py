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

    # Get cache configuration
    print("\nCache Configuration:")
    print("Available mapping types:")
    print("  1. Direct Mapped")
    print("  2. Fully Associative")
    print("  3. Set Associative")

    mapping_choice = input("Select mapping type (1/2/3) [default: 2]: ").strip()
    if mapping_choice == '1':
        mapping_type = "direct_mapped"
        num_sets = None
    elif mapping_choice == '3':
        mapping_type = "set_associative"
        num_sets_input = input("Enter number of sets [default: 4]: ").strip()
        try:
            num_sets = int(num_sets_input) if num_sets_input else 4
            if num_sets <= 0:
                print("Invalid number of sets. Using default: 4")
                num_sets = 4
        except ValueError:
            print("Invalid input. Using default: 4")
            num_sets = 4
    else:
        mapping_type = "fully_associative"
        num_sets = None

    hierarchy = Heir(
        l1_size=32,
        l2_size=128,
        l3_size=512,
        policy="LRU",
        block_size=1,
        mapping_type=mapping_type,
        num_sets=num_sets
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
