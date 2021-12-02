#!/usr/bin/python

# Esto no es un buen ejemplo de desarollo de codigo!!
# Ni siquier lo voy a firmar :-)
# El objetivo es que fuese funcional

from tkinter import *
from tkinter import ttk
import math
from time import sleep
from utils import (
    create_dir,
    parse_network_file,
    get_gpg,
    get_fingerprints,
    parse_config_file,
    Event,
    LOCALHOST,
    BUFSIZE,
    LogService,
    Log,
)
from collections import OrderedDict

MaxCombos= 1
pos = 0

def NextEntry():
    global pos
    
    if (pos == 0):
        print("Dato: ", tipoDato_cb.get())
        print("Transac/block", entry_transaccion_bloque.get())

        print("Time Ini", tsi.get())
        print("Time Fin", tsf.get())

        print("Acciones: ", tipoAccion_cb.get())
        print("------\n\n")

    print("Procesando log: " + entradas[pos])

    print(node_cbs)

    for (i, j) in node_cbs:
        if i.get() == entradas[pos] or len(node_cbs) == 1:
            j.config(state=NORMAL)

            if(tipoAccion_cb.get() == 'Presentacion'):
                while pos <= len(event_logs):
                    if "PRESENTATION" in event_logs[pos] or "PRESENTATION_ACK" in event_logs[pos]:
                        j.insert(END, event_logs[pos]+"\n\n")
                        break
                    pos = pos + 1
            elif(tipoAccion_cb.get() == 'Transacción Nueva'):
                while pos <= len(event_logs):
                    if "NEW_TRANSACTION" in event_logs[pos] or "NEW_TRANSACTION_ACK" in event_logs[pos]:
                        j.insert(END, event_logs[pos]+"\n\n")
                        break
                    pos = pos + 1
            elif(tipoAccion_cb.get() == 'Transacción Propaga'):
                while pos <= len(event_logs):
                    if "TRANSACTION" in event_logs[pos] or "TRANSACTION_ACK" in event_logs[pos]:
                        j.insert(END, event_logs[pos]+"\n\n")
                        break
                    post = post + 1
            elif(tipoAccion_cb.get() == 'Bloque Propaga'):
                while pos <= len(event_logs):
                    if "BLOCK" in event_logs[pos] or "BLOCK_ACK" in event_logs[pos]:
                        j.insert(END, event_logs[pos]+"\n\n")
                        break
                    pos = pos + 1
            else:
                j.insert(END, event_logs[pos]+"\n\n")
                pos = pos + 1
            # j.insert(END,"Acc:"+str(pos)+":\n " +entradas[pos]+"\n\n")
            j.config(state=DISABLED)

# lee los archivos y saca la informacion
# ESTO ES UN STUB, AQUI DEBE AGREGAR CODIGO APROPIADO
def leer(d):
    # obtiene nombre nodos
    global nodeNames, fechaI, fechaF, entradas, event_logs

    nodeNames = ('nodo1', 'nodo2', 'nodo3', 'nodo4', 'nodo5', 'nodo6',
                 'nodo7', 'nodo8', 'nodo9', 'nodo10', 'nodo11',
                 'nodo12', 'nodo13', 'nodo14', 'nodo15', 'nodo16',
                 'nodo17', 'nodo18', 'nodo19' , 'nodo20')

    # obtiene entradas de del log

    logs = OrderedDict()
    for nodo in nodeNames:
        parse_log_file(d + nodo + '.log', logs, nodo)

    logs = OrderedDict(sorted(logs.items()))
    els = list(logs.items())
    fechaI = els[0][0].strftime("%Y/%m/%d %H:%M:%S")
    fechaF = els[-1][0].strftime("%Y/%m/%d %H:%M:%S")

    entradas = [ ]
    event_logs = [ ]

    for i in logs:
        entradas.append((logs[i]["nodo"]))
        event_logs.append((logs[i]["log_event"]))
        
def getNodeNames():
    return nodeNames

    
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
        data_type_sv = StringVar()
        data_type_cb = ttk.Combobox(top_frame, textvariable=data_type_sv)
        data_type_cb["values"] = data_type_values
        data_type_cb.current(0)
        data_type_cb["state"] = "readonly"
        data_type_cb.grid(row=0, column=1)

        value_lb = Label(top_frame, text="Valor (opc): ")
        value_lb.grid(row=1, column=0)

        tx_block_entry = Entry(top_frame, background="red")
        tx_block_entry.grid(row=1, column=1)

        ts_start_lb = Label(top_frame, text="Tiempo Inicio: ")
        ts_start_lb.grid(row=0, column=3)
        ts_end_lb = Label(top_frame, text="Tiempo Final: ")
        ts_end_lb.grid(row=1, column=3)

        ts_start_sv = StringVar()
        ts_start_entry = Entry(top_frame, background="pink", textvariable=ts_start_sv)
        ts_start_entry.grid(row=0, column=4)

        ts_end_sv = StringVar()
        ts_end_entry = Entry(top_frame, background="pink", textvariable=ts_end_sv)
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


    def next_logs(self):
        if self.logs_iterator is None:
            self.logs_iterator = iter(self.logs_service)
            self.last_log = next(self.logs_iterator, None)
        next_log = next(self.logs_iterator, None)
        while self.last_log is not None:
            for i, node_sv in enumerate(self.node_svs):
                if node_sv.get() == next_log.name:
                    self.node_entries[i].insert(END, str(next_log) + "\n")
            next_log = next(self.logs_iterator, None)
            if next_log is None or self.last_log.dt != next_log.dt:
                break
            else:
                self.last_log = next_log
        self.last_log = next_log


        


nodeNames = ()

d = sys.argv[1]

root = Tk()

app = Application(root, d)

if sys.argv[2] == "-mt":
    r = app.make_interfaz(1, 1)
else:
    r = app.make_interfaz(4, 4)

r.mainloop()
