import tkinter as tk
from tkinter import ttk, messagebox
from io import StringIO
from contextlib import redirect_stdout
from heirarchy import Heir
from GenTrace import generate_trace, remove_trace

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

class CacheSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CEC 470 Cache Simulator")

        main_frame = ttk.Frame(root, padding=10)
        # print(main_frame)
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="L1 size:").grid(row=0, column=0, sticky="w")
        self.l1_var = tk.StringVar(value="32")
        ttk.Entry(main_frame, textvariable=self.l1_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(main_frame, text="L2 size:").grid(row=1, column=0, sticky="w")
        # self.l1_var = tk.StringVar(n)
        self.l2_var = tk.StringVar(value="128")
        ttk.Entry(main_frame, textvariable=self.l2_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(main_frame, text="L3 size:").grid(row=2, column=0, sticky="w")
        self.l3_var = tk.StringVar(value="512")
        ttk.Entry(main_frame, textvariable=self.l3_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(main_frame, text="Policy:").grid(row=3, column=0, sticky="w")
        self.policy_var = tk.StringVar(value="LRU")
        policy_combo = ttk.Combobox(main_frame, textvariable=self.policy_var, values=["FIFO", "LRU", "RANDOM", "LFU"], width=10,state="readonly")
        policy_combo.grid(row=3, column=1, sticky="w")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 5), sticky="w")

        ttk.Button(button_frame, text="Generate Trace", command=self.on_generate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear Trace", command=self.on_clear).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Simulate", command=self.on_run).grid(row=0, column=2, padx=5)

        self.output = tk.Text(main_frame, width=70, height=20)
        self.output.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def on_generate(self):
        generate_trace()
        # generate_trace(title = "TraceFile.txt")

        messagebox.showinfo("Trace", "Generated new TraceFile.txt")

    def on_clear(self):
        remove_trace()
        messagebox.showinfo("Trace", "TraceFile.txt cleared")

    def on_run(self):
        # try:
        l1 = int(self.l1_var.get())
        l2 = int(self.l2_var.get())
        
        l3 = int(self.l3_var.get())
        # except ValueError:
        #     messagebox.showerror("Error", "Cache sizes must be integers.")
        #     return

        policy = self.policy_var.get()

        try:
            blocks = load_trace("TraceFile.txt")
        except FileNotFoundError:
            messagebox.showerror("Error", "Trace File doesn't exist. Generate a new one first")
            return

        if not blocks:
            messagebox.showerror("Error", "Trace File doesn't exist. Generate a new one first")
            return

        hierarchy = Heir(
            l1_size=l1,
            l2_size=l2,
            l3_size=l3,
            policy=policy,
            block_size=1
        )

        for b in blocks:
            hierarchy.access(b)

        buf = StringIO()
        with redirect_stdout(buf):
            hierarchy.print_stats()
        stats_text = buf.getvalue()

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, stats_text)

        hierarchy.export_csv("results_gui.csv")
        self.output.insert(tk.END, f"\n\nStats also exported to results_gui.csv")

def run_gui():
    root = tk.Tk()
    app = CacheSimGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
