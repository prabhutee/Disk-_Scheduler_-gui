import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Disk Scheduling Algorithms
def calculate_seek_time(schedule):
    total = sum(abs(schedule[i] - schedule[i-1]) for i in range(1, len(schedule)))
    avg = total / (len(schedule)-1) if len(schedule) > 1 else 0
    return total, avg

def fcfs(requests, head, _=0):
    return [head] + requests

def sstf(requests, head, _=0):
    reqs = requests.copy()
    sequence = [head]
    while reqs:
        closest = min(reqs, key=lambda x: abs(x - head))
        sequence.append(closest)
        head = closest
        reqs.remove(closest)
    return sequence

def scan(requests, head, disk_size):
    reqs = sorted(requests + [0, disk_size-1])
    idx = reqs.index(head) if head in reqs else sorted(reqs + [head]).index(head)
    return reqs[idx:] + reqs[:idx][::-1]

def cscan(requests, head, disk_size):
    reqs = sorted(requests + [0, disk_size-1])
    idx = reqs.index(head) if head in reqs else sorted(reqs + [head]).index(head)
    return reqs[idx:] + reqs[:idx]

def look(requests, head, _=0):
    reqs = sorted(requests)
    idx = reqs.index(head) if head in reqs else sorted(reqs + [head]).index(head)
    return reqs[idx:] + reqs[:idx][::-1]

def clook(requests, head, _=0):
    reqs = sorted(requests)
    idx = reqs.index(head) if head in reqs else sorted(reqs + [head]).index(head)
    return reqs[idx:] + reqs[:idx]

# Algorithm dictionary (MUST come before class definition)
ALGORITHMS = {
    "FCFS": fcfs,
    "SSTF": sstf,
    "SCAN": scan,
    "C-SCAN": cscan,
    "LOOK": look,
    "C-LOOK": clook
}

class DiskSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Simulator")
        self.root.state('zoomed')  # Start maximized
        self.setup_styles()
        self.setup_ui()
        self.setup_plot()
        self.setup_menu()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('.', font=('Arial', 12))
        self.style.configure('TLabel', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12, 'bold'))
        self.style.configure('TLabelFrame', font=('Arial', 14, 'bold'))
        self.style.configure('TEntry', font=('Arial', 12))

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding=15)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(input_frame, text="Disk Size (1-10000):").grid(row=0, column=0, sticky="w", pady=5)
        self.disk_size = ttk.Entry(input_frame, width=20)
        self.disk_size.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(input_frame, text="Initial Head (0 - DiskSize-1):").grid(row=1, column=0, sticky="w", pady=5)
        self.head = ttk.Entry(input_frame, width=20)
        self.head.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(input_frame, text="Requests (comma-separated):").grid(row=2, column=0, sticky="w", pady=5)
        self.requests = ttk.Entry(input_frame, width=40)
        self.requests.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(input_frame, text="Algorithms:").grid(row=3, column=0, sticky="w", pady=5)
        self.algo_list = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, height=6, 
                                  font=('Arial', 12), bg='#f0f0f0')
        for algo in ALGORITHMS:
            self.algo_list.insert(tk.END, algo)
        self.algo_list.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Run", command=self.run).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Compare All", command=self.compare_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)

        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=15)
        results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=10, 
                                                    font=('Consolas', 11), wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        input_frame.columnconfigure(1, weight=1)

    def setup_plot(self):
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.fig, self.ax = plt.subplots(figsize=(12, 6), dpi=100)
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_menu(self):
        menu_bar = tk.Menu(self.root, font=('Arial', 12))
        help_menu = tk.Menu(menu_bar, tearoff=0, font=('Arial', 12))
        help_menu.add_command(label="Algorithm Info", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def detailed_seek_sequence(self, schedule):
        detailed = []
        for i in range(1, len(schedule)):
            from_track = schedule[i-1]
            to_track = schedule[i]
            seek = abs(to_track - from_track)
            detailed.append(f"Step {i}: {from_track} → {to_track} ({seek} cylinders)")
        return detailed

    def validate_inputs(self):
        try:
            disk_size = int(self.disk_size.get())
            head = int(self.head.get())
            raw_requests = self.requests.get().replace(' ', '')
            requests = list(map(int, raw_requests.split(',')))
            
            if not (1 <= disk_size <= 10000):
                raise ValueError("Disk size must be between 1-10000")
                
            if not (0 <= head < disk_size):
                raise ValueError(f"Head position must be between 0-{disk_size-1}")
                
            if any(not (0 <= r < disk_size) for r in requests):
                raise ValueError(f"All requests must be between 0-{disk_size-1}")
                
            selected_algos = self.algo_list.curselection()
            if not selected_algos:
                raise ValueError("Select at least one algorithm")
                
            return disk_size, head, requests, selected_algos
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return None

    def run(self):
        inputs = self.validate_inputs()
        if not inputs:
            return
            
        disk_size, head, requests, algo_indices = inputs
        self.results_text.delete(1.0, tk.END)
        self.ax.clear()
        
        results = []
        for idx in algo_indices:
            algo_name = self.algo_list.get(idx)
            algo_func = ALGORITHMS[algo_name]
            schedule = algo_func(requests.copy(), head, disk_size)
            total, avg = calculate_seek_time(schedule)
            details = self.detailed_seek_sequence(schedule)
            
            results.append(
                f"\n{'='*60}\n"
                f"{algo_name} SCHEDULE DETAILS\n"
                f"{'='*60}\n"
                f"Full Sequence: {' → '.join(map(str, schedule))}\n\n"
                "Step-by-Step Movements:\n" + '\n'.join(details) + "\n\n"
                f"Total Seek Distance: {total} cylinders\n"
                f"Average Seek Distance: {avg:.2f} cylinders\n"
                f"{'-'*60}"
            )
            
            # Plot configuration
            self.ax.plot(schedule, label=algo_name, marker='o', markersize=6)
            self.ax.set_xticks(range(len(schedule)))
            self.ax.set_xticklabels([str(i+1) for i in range(len(schedule))], rotation=45)
            self.ax.set_xlabel("Request Order", fontsize=12)
            self.ax.set_ylabel("Cylinder Number", fontsize=12)
            self.ax.set_title("Disk Scheduling Comparison", fontsize=14)
            self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            self.ax.grid(True, linestyle='--', alpha=0.6)
            self.fig.tight_layout()

        self.results_text.insert(tk.END, '\n'.join(results))
        self.canvas.draw()

    def compare_all(self):
        self.algo_list.selection_clear(0, tk.END)
        for i in range(len(ALGORITHMS)):
            self.algo_list.selection_set(i)
        self.run()

    def reset(self):
        self.disk_size.delete(0, tk.END)
        self.head.delete(0, tk.END)
        self.requests.delete(0, tk.END)
        self.algo_list.selection_clear(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.ax.clear()
        self.canvas.draw()

    def show_help(self):
        help_text = """Disk Scheduling Algorithms:

FCFS (First-Come First-Served):
- Services requests in arrival order
- Simple but often poor performance

SSTF (Shortest Seek Time First):
- Selects nearest request to current head position
- Can cause starvation

SCAN (Elevator Algorithm):
- Moves in one direction to end, then reverses
- Services requests along the way

C-SCAN (Circular SCAN):
- Moves in one direction to end, then
- Jumps to start and continues same direction

LOOK:
- Similar to SCAN but reverses at last request
- instead of physical end of disk

C-LOOK:
- Circular version of LOOK algorithm"""
        
        help_window = tk.Toplevel()
        help_window.title("Algorithm Information")
        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, 
                                       font=('Arial', 11), width=80, height=25)
        text.insert(tk.INSERT, help_text)
        text.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulingApp(root)
    root.mainloop()



