#!/usr/bin/python

# Esto no es un buen ejemplo de desarollo de codigo!!
# Ni siquier lo voy a firmar :-)
# El objetivo es que fuese funcional

from tkinter import *
from tkinter import ttk
import math
import datetime
import random

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

    for (i, j) in node_cbs:
        if i.get() == entradas[pos] or len(node_cbs) == 1:
            j.config(state=NORMAL)
            j.insert(END,"Acc:"+str(pos)+":\n " +entradas[pos]+"\n\n")
            j.config(state=DISABLED)

    pos = pos + 1

# lee los archivos y saca la informacion
# ESTO ES UN STUB, AQUI DEBE AGREGAR CODIGO APROPIADO
def leer(d):
    # obtiene nombre nodos
    global nodeNames, fechaI, fechaF, entradas

    nodeNames = ('node0', 'node1', 'node2', 'node3', 'node4', 'node5',
                 'node6', 'node7', 'node8', 'node9', 'node10',
                 'node11', 'node12', 'node13', 'node14', 'node15',
                 'node16', 'node17', 'node18' , 'node19')

    fechaI = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    fechaF = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    # obtiene entradas de del log

    entradas = [ ]

    for i in range(100):
        r = random.randint(0,len(nodeNames))
        entradas.append(('node'+str(r)))

        
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

if sys.argv[3] == "-mt":
    r = app.make_interfaz(1, 1)
else:
    r = app.make_interfaz(4, 4)

r.mainloop()
