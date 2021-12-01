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
    parse_log_file,
    Event,
    LOCALHOST,
    BUFSIZE,
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
    def __init__(self, parent):
        self.parent = parent

    def make_interfaz(self, f, c):
        global asociacionCombo
        
        root.title('Model Definition')
        root.geometry('{}x{}'.format(1250, 850))

        # create all of the main containers
        top_frame = Frame(root, bg='green', width=800, height=50, pady=3)
        center    = Frame(root, bg='blue', width=800, height=550, padx=3, pady=3)

        # layout all of the main containers
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=1)
        root.grid_rowconfigure(4, weight=2)
        root.grid_rowconfigure(5, weight=1)
        root.grid_rowconfigure(6, weight=2)
        root.grid_rowconfigure(7, weight=1)
        root.grid_rowconfigure(8, weight=2)
        root.grid_rowconfigure(9, weight=1)
        root.grid_rowconfigure(10, weight=2)

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)

        top_frame.grid(row=0, sticky="ew", rowspan=2)
        center.grid(row=2, rowspan=8, columnspan=4, sticky="nsew")

        global tipoDato_cb, entry_transaccion_bloque
        datoValores = ('Todos', 'Bloques', 'Transacciones')
        self.tipoDatoSelected = StringVar()
        tipoDato_cb = ttk.Combobox(top_frame, textvariable=self.tipoDatoSelected)
        tipoDato_cb['values'] = datoValores
        tipoDato_cb.current(0)

        tipoDato_cb['state'] = 'readonly'  # normal

        tipoDato_cb.grid(row=0, column=1)
       
        model_label  = Label(top_frame, text='Seleccione: ')
        val_label  = Label(top_frame, text='Valor(Opc): ')
        entry_transaccion_bloque      = Entry(top_frame, background="red")
        
        # layout the widgets in the top frame

        model_label.grid(row=0, column=0)
        val_label.grid(row=1, column=0)
        entry_transaccion_bloque.grid(row=1, column=1)

        global tipoAccion_cb
        accionValores = ('Todos', 'Presentacion', 'Transacción Nueva', 'Transacción Propaga', 'Bloque Propaga' )
        self.tipoAccionSelected = StringVar()
        tipoAccion_cb = ttk.Combobox(top_frame, textvariable=self.tipoAccionSelected)
        tipoAccion_cb['values'] = accionValores
        tipoAccion_cb.current(0)

        tipoAccion_cb['state'] = 'readonly'  # normal

        tipoAccion_cb.grid(row=0, column=2)
       
        # layout the widgets in the top frame

        timeStampIni_label  = Label(top_frame, text='Tiempo Inico: ')
        timeStampFin_label  = Label(top_frame, text='Tiempo Final: ')

        timeStampIni_label.grid(row=0, column=3)
        timeStampFin_label.grid(row=1, column=3)
        global tsi, tsf
        tsie = StringVar()
        tsfe = StringVar()

        tsi = Entry(top_frame, background="pink", textvariable=tsie)
        tsf = Entry(top_frame, background="pink", textvariable=tsfe)
        tsi.grid(row=0, column=4)
        tsf.grid(row=1, column=4)

        tsie.set(fechaI)
        tsfe.set(fechaF)

        botonGo = Button(top_frame, text='Next', bg='cyan', command=NextEntry)

        botonGo.grid(column=3, row=2)

        # create the widgets for the bottom frame
        hei = math.trunc(40/f)
        wid = math.trunc(153/c)
        
        k = 0
        global node_cbs
        node_cbs = []
        for j in range(1,f*2,2):
            for i in range(c):        
                nodes = getNodeNames()

                self.selected_Node = StringVar()
                node_cb = ttk.Combobox(center, textvariable=self.selected_Node)
                
                node_cb['values'] = nodes
                node_cb['state'] = 'readonly'  # normal
             
                node_cb.grid(row =2+j, column =i)
        
                entry = Text(center, height = hei, width = wid)
                entry.config(state=DISABLED)

                entry.grid(row=3+j, column=i)
                k = k + 1

                node_cbs.append((node_cb, entry))
                

        MaxCombos = 1
        if (f > 1):
            MaxCombos = 16

        k= 0
        for (i, j) in node_cbs[0:MaxCombos]:
            i.current(k)
            k=k+1
        
        return root

nodeNames = ()

d = sys.argv[1]

# Leer logs
leer(d)

root = Tk()

app = Application(root)

if sys.argv[2] == "-mt":
    r = app.make_interfaz(1, 1)
else:
    r = app.make_interfaz(4, 4)

r.mainloop()
