#!/usr/bin/python

# Esto no es un buen ejemplo de desarollo de codigo!!
# Ni siquier lo voy a firmar :-)
# El objetivo es que fuese funcional

from tkinter import *
from tkinter import ttk
import math
from datetime import datetime
from utils import LogService, Log
    

class Application:
    def __init__(self, root: Tk, logs_dir):
        self.root = root
        self.root.title("Visualizer")
        self.logs_service = LogService(logs_dir)
        self.logs_iterator = None
        self.last_log = None


    def make_interfaz(self, rows, cols):
        self.root.geometry('{}x{}'.format(1250, 850))

        self.root.geometry(f"{1250}x{850}")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        # Top frame
        top_frame = Frame(self.root, background="green", width=800, height=50, pady=3)
        top_frame.grid(row=0, sticky="ew")

        model_lb = Label(top_frame, text="Seleccione: ")
        model_lb.grid(row=0, column=0)

        data_type_values = ("Todos", "Bloques", "Transacciones")
        self.data_type_sv = StringVar()
        self.data_type_cb = ttk.Combobox(top_frame, textvariable=self.data_type_sv)
        self.data_type_cb.bind("<<ComboboxSelected>>", self.data_type_change)
        self.data_type_cb["values"] = data_type_values
        self.data_type_cb.current(0)
        self._data_type = self.data_type_sv.get()
        self.data_type_cb["state"] = "readonly"
        self.data_type_cb.grid(row=0, column=1)

        event_type_values = tuple(self.logs_service.ALL_EVENTS)
        event_type_values = ("Todos",) + event_type_values
        self.event_type_sv = StringVar()
        self.event_type_cb = ttk.Combobox(top_frame, textvariable=self.event_type_sv)
        self.event_type_cb.bind("<<ComboboxSelected>>", self.event_type_change)
        self.event_type_cb["values"] = event_type_values
        self.event_type_cb.current(0)
        self._event_type = self.event_type_sv.get()
        self.event_type_cb["state"] = "readonly"
        self.event_type_cb.grid(row=0, column=2)

        value_lb = Label(top_frame, text="Valor (opc): ")
        value_lb.grid(row=1, column=0)

        self.tx_block_entry = ttk.Entry(top_frame, background="red")
        self.tx_block_entry.grid(row=1, column=1)
        self.tx_block_entry.bind("<Return>", self.data_type_change)

        ts_start_lb = Label(top_frame, text="Tiempo Inicio: ")
        ts_start_lb.grid(row=0, column=3)
        ts_end_lb = Label(top_frame, text="Tiempo Final: ")
        ts_end_lb.grid(row=1, column=3)

        self.ts_start_sv = StringVar()
        self.ts_start_sv.set(str(self.logs_service.log_start))
        self._ts_start_value = self.ts_start_sv.get()
        ts_start_entry = Entry(top_frame, background="pink", textvariable=self.ts_start_sv)
        ts_start_entry.grid(row=0, column=4)

        self.ts_end_sv = StringVar()
        self.ts_end_sv.set(str(self.logs_service.log_end))
        self._ts_end_value = self.ts_end_sv.get()
        ts_end_entry = Entry(top_frame, background="pink", textvariable=self.ts_end_sv)
        ts_end_entry.grid(row=1, column=4)

        next_btn = Button(top_frame, text="Next", bg="cyan", command=self.next_logs)
        next_btn.grid(row=2, column=3)


        # ttk.Label(top_frame, text="Hello World!").grid(column=0, row=0)
        # ttk.Button(top_frame, text="Quit", command=self.root.destroy).grid(column=1, row=0)

        # Center frame
        center_frame = Frame(self.root, background="blue", width=800, height=550, padx=3, pady=3)
        center_frame.grid(row=1, columnspan=4, sticky="nsew")

        height = math.trunc(40/rows)
        width = math.trunc(153/cols)

        node_names = self.logs_service.log_names()

        iterator = iter(node_names)

        finish = False
        self.node_svs = []
        self.node_entries = []
        for i in range(0, rows):
            for j in range(0, cols):
                node_name = next(iterator, None)
                if node_name is None:
                    finish = True
                    break
                node_sv = StringVar()
                node_cb = ttk.Combobox(center_frame, textvariable=node_sv)
                node_cb["values"] = node_names
                node_cb["state"] = "readonly"
                node_cb.grid(row=i*2, column=j)
                node_cb.current(i * rows + j)

                entry = Text(center_frame, height=height, width=width)
                # entry.config(state=DISABLED)
                entry.grid(row=i*2+1, column=j)
                # scrollbar = ttk.Scrollbar(center_frame, command=entry.yview)
                # scrollbar.grid(row=i*2+1, column=j*2+1, sticky="nsew")
                # entry["yscrollcommand"] = scrollbar.set
                self.node_svs.append(node_sv)
                self.node_entries.append(entry)
            if finish:
                break
        
        return self.root


    def data_type_change(self, virtual_event):
        """Set the logs iterator upon data type change"""
        data_type = self.data_type_sv.get()
        if self._data_type == data_type:
            return
        self._data_type = data_type
        if data_type == "Todos":
            # Reset to default
            self.logs_iterator = None
        else:
            if data_type == "Bloques":
                log_files = self.logs_service.find_logs_by_op_type("block", self.tx_block_entry.get())
            elif data_type == "Transacciones":
                log_files = self.logs_service.find_logs_by_op_type("transaction", self.tx_block_entry.get())
            composed_logs: List[Log] = []
            for logs in log_files.values():
                composed_logs += logs
            self.logs_iterator = iter(sorted(composed_logs))
            self.last_log = next(self.logs_iterator, None)
        self.reset_log_entries()
        self.event_type_cb.current(0)
        self.ts_end_sv.set(str(self.logs_service.log_end))
        self._ts_end_value = self.ts_end_sv.get()
        self.ts_start_sv.set(str(self.logs_service.log_start))
        self._ts_start_value = self.ts_start_sv.get()


    def event_type_change(self, virtual_event):
        event_type = self.event_type_sv.get()
        if self._event_type == event_type:
            return
        self._event_type = event_type
        if event_type == "Todos":
            # Reset to default
            self.logs_iterator = None
        else:
            log_files = self.logs_service.find_logs_by_op(event_type, self.tx_block_entry.get())
            composed_logs: List[Log] = []
            for logs in log_files.values():
                composed_logs += logs
            self.logs_iterator = iter(sorted(composed_logs))
            self.last_log = next(self.logs_iterator, None)
        self.reset_log_entries()
        self.data_type_cb.current(0)
        self.ts_end_sv.set(str(self.logs_service.log_end))
        self._ts_end_value = self.ts_end_sv.get()
        self.ts_start_sv.set(str(self.logs_service.log_start))
        self._ts_start_value = self.ts_start_sv.get()


    def reset_log_entries(self):
        for entry in self.node_entries:
            entry.delete("1.0", "end")


    def check_timestamp_entries(self):
        if self._ts_start_value != self.ts_start_sv.get() or self._ts_end_value != self.ts_end_sv.get():
            self._ts_start_value = self.ts_start_sv.get()
            self._ts_end_value = self.ts_end_sv.get()
            start_date = datetime.strptime(self._ts_start_value, "%Y-%m-%d %H:%M:%S.%f")
            end_date = datetime.strptime(self._ts_end_value, "%Y-%m-%d %H:%M:%S.%f")
            log_files = self.logs_service.find_logs_by_timestamp_range(start_date, end_date)
            composed_logs: List[Log] = []
            for logs in log_files.values():
                composed_logs += logs
            self.logs_iterator = iter(sorted(composed_logs))
            self.last_log = next(self.logs_iterator, None)
            self.event_type_cb.current(0)
            self.data_type_cb.current(0)
            self.reset_log_entries()


    def next_logs(self):
        self.check_timestamp_entries()
        if self.logs_iterator is None:
            self.logs_iterator = iter(self.logs_service)
            self.last_log = next(self.logs_iterator, None)
        next_log = next(self.logs_iterator, None)
        while self.last_log is not None:
            for i, node_sv in enumerate(self.node_svs):
                if node_sv.get() == self.last_log.name:
                    self.node_entries[i].insert(END, str(self.last_log) + "\n")
            if next_log is None or self.last_log.dt != next_log.dt:
                break
            self.last_log = next_log
            next_log = next(self.logs_iterator, None)
        self.last_log = next_log


d = sys.argv[1]

root = Tk()

app = Application(root, d)

if sys.argv[2] == "-mt":
    r = app.make_interfaz(1, 1)
else:
    r = app.make_interfaz(4, 4)

r.mainloop()
