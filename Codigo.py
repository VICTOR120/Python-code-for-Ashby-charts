"""
ECUADOR
Quito, junio 2018

ESCUELA POLITÉCNICA NACIONAL
FACULTAD DE INGNIERIA MECÁNICA

TRABAJO DE TITULACIÓN PREVIO A LA OBTENCIÓN DEL TÍTULO DE INGENIERO MECÁNICO

Tesistas:
    Chiriboga del Valle Cristhian Leonardo
    Obando Martínez Esteban Andrés
    
Director:
    Ing. Hidalgo Díaz Víctor Hugo, DSc
    
Co-Director:
    Ing. Granja Ramírez Mario Germán, MSc
"""

import wx
import numpy as np

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.axes import Subplot
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

'lectura de datos y grafico de rangos'
import matplotlib.patches as patches
import xlrd as xl

'gráfico de regiones'
from matplotlib.path import Path
from scipy.spatial import ConvexHull

class GUI_ASHBY(wx.Frame):
    def __init__(self, parent, title):
        super(GUI_ASHBY, self).__init__(parent, title=title, size=(800,600))
        self.SetBackgroundColour('white')   #es necesario fondo blanco para que no se vea cuando se carga la ventana 
        self.tabla=self.importacion_datos() #Importación de datos (7 regiones) desde la base al iniciar la interfaz  
        self.Maximize()
        self.InitUI()
        icono=wx.Icon("EPNi.ico")   #guarda el incono en una variable
        self.SetIcon(icono) #agrega el icono a la ventana de la interfaz
        self.Show() #muestra la interfaz en la pantalla

    def enter_axes(self, event):
        print ('dentro')
        self.cid=self.fig.canvas.mpl_connect('button_press_event',self.Graficar_rectaIndice)    #conecta el evento clic sobre la figura
        self.clic="in"
        
    def leave_axes(self, event):
        print ('fuera')
        self.clic="out"

        
    def InitUI(self):
        self.splitter = wx.SplitterWindow(self, -1)  #divide la ventana en dos secciones
        'Crea el panel donde estarán los controles'
        self.panel_controles = wx.Panel(self.splitter, -1, size=(20, -1), style=wx.BORDER_SUNKEN)
        self.panel_controles.SetBackgroundColour(wx.WHITE)
        'Crea el panel para graficar los diagramas de Ashby'
        self.panel_grafico = wx.Panel(self.splitter, -1, style=wx.BORDER_SUNKEN)
        self.panel_grafico.SetBackgroundColour('white')
        'posiciona los paneles dentro de las secciones de la ventana'
        self.splitter.SplitVertically(self.panel_controles, self.panel_grafico)
        self.splitter.SetMinimumPaneSize(300)
        self.splitter.SetSashPosition(1,300)

        #===============MODIFICACIÓN DE "PANEL_GRAFICO"=============
        box_grafico=wx.BoxSizer(wx.VERTICAL)
        'Creción del área donde se dibujarán los diagramas de Ashby'
        self.fig = Figure(facecolor='PowderBlue')
        self.canvas = FigureCanvasWxAgg(self.panel_grafico, -1, self.fig)
        self.ax = self.fig.add_axes([0.08,0.1,0.86,0.8])
        self.ax.autoscale(True)
        self.ax.semilogx()
        self.ax.semilogy()
        self.ax.grid(True)
        
        box_grafico.Add(self.canvas,1, wx.EXPAND| wx.ALL, 10 )  #configura la figura para que se expanda con la ventana
        self.panel_grafico.SetSizer(box_grafico)    #agrega la figura al panel_grafico

##        self.cid=self.fig.canvas.mpl_connect('button_press_event',self.Graficar_rectaIndice)    #conecta el evento clic sobre la figura
        self.fig.canvas.mpl_connect('axes_enter_event',self.enter_axes)    #conecta el evento clic sobre la figura
        self.fig.canvas.mpl_connect('axes_leave_event',self.leave_axes)    #conecta el evento clic sobre la figura

        #===================CREACIÓN DE PANELES===================
        #   PANEL OPCIONES
        #pl_opciones: panel que contiene 2 toggleButtons(regiones y nombres) y un 1 botón (Graficar)
        pl_opciones=wx.Panel(self.panel_controles,-1,size=(-1,60))
        pl_opciones.SetBackgroundColour('grey')

        #   PANEL MATERIALES
        #pl_materiales: contiene las opciones para graficar la familia, propiedades, parámetrose y selección de índice
        pl_materiales=wx.Panel(self.panel_controles,-1,size=(-1,450))
        pl_materiales.SetBackgroundColour('wheat')

        #   PANEL ARBOL DE MATERIALES
        #pl_arbol: contiene la lista de materiales que cumplen con los parámetros dados
        pl_arbol=wx.Panel(self.panel_controles,-1,size=(-1,60))
        pl_arbol.SetBackgroundColour('wheat')

        #==================CREACIÓN DE OBJETOS DENTRO DE CADA PANEL==============
        #   **SOBRE PANEL OPCIONES**
        
        'SECCIÓN: Botones de mando'
            #ToggleButtons
        self.tb_regiones=wx.ToggleButton(pl_opciones,-1,label='Regiones',pos=(120,15),size=(70,25))
        self.tb_nombres=wx.ToggleButton(pl_opciones,-1,label='Nombres',pos=(200,15),size=(70,25))
            #Button
        self.b_graficar=wx.Button(pl_opciones,-1,label='GRAFICAR',pos=(5,5),size=(100,50))

        #   **SOBRE PANEL MATERIALES**
        
        'SECCIÓN: Selección de índice'
            #ToggleButton
        self.tb_indice=wx.ToggleButton(pl_materiales,-1,label='Graficar índice',pos=(150,30),size=(85,25))
            #StaticBox
        wx.StaticBox(pl_materiales, -1, 'Indice', pos=(135, 10), size=(120, 130))
            #SpinControl
        self.sc_indice=wx.SpinCtrl(pl_materiales,-1,'',pos=(150,90),size=(40,-1))
        self.sc_indice.SetRange(1,3)
            #ComboBox
        lista_filtro=['Superior','Inferior','Sobre línea']
        self.cmbo_filtro=wx.ComboBox(pl_materiales, -1, pos=(150, 60), size=(85, 25),
                                     choices=lista_filtro,
                                     style=wx.CB_READONLY)
        
        'SECCIÓN: Selección de familias'
            #ChecBox
        self.cb_todo=wx.CheckBox(pl_materiales,id=4,label='Graficar todo',pos=(25,10))
        self.cb_metales=wx.CheckBox(pl_materiales,id=5,label='Metales',pos=(35,30))
        self.cb_ceramicos=wx.CheckBox(pl_materiales,id=6,label='Cerámicos',pos=(35,50))
        self.cb_compuestos=wx.CheckBox(pl_materiales,id=7,label='Compuestos',pos=(35,70))
        self.cb_polimeros=wx.CheckBox(pl_materiales,id=8,label='Polímeros',pos=(35,90))
        self.cb_elastomeros=wx.CheckBox(pl_materiales,id=9,label='Elastómeros',pos=(35,110))
        self.cb_espumas=wx.CheckBox(pl_materiales,id=10,label='Espumas',pos=(35,130))
        self.cb_naturales=wx.CheckBox(pl_materiales,id=11,label='Naturales',pos=(35,150))
            #color de fondo
        self.cb_metales.SetBackgroundColour('red')
        self.cb_ceramicos.SetBackgroundColour('yellow')
        self.cb_compuestos.SetBackgroundColour('brown')
        self.cb_polimeros.SetBackgroundColour('blue')
        self.cb_elastomeros.SetBackgroundColour('cyan')
        self.cb_espumas.SetBackgroundColour('green')
        self.cb_naturales.SetBackgroundColour('DimGrey')
        
        'SECCIÓN: Selección de propieadades'
            #ComboBox
        lista_materiales=['Módulo de young','Densidad','Resistencia mecánica',
                          'Conductividad térmica','Coef. dilatación térmica',
                          'Temp. máx. de servicio']
        self.cmbo_prop_x=wx.ComboBox(pl_materiales, -1, pos=(50, 180), size=(130, -1),
                                     choices=lista_materiales,
                                     style=wx.CB_READONLY)
        self.cmbo_prop_y=wx.ComboBox(pl_materiales, -1, pos=(50, 210), size=(130, -1),
                                     choices=lista_materiales,
                                     style=wx.CB_READONLY)
            #StaticText
        self.lb_ejex=wx.StaticText(pl_materiales, -1, 'Eje x:',pos=(20, 182))
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Eje y:',pos=(20, 212))
        
        'SECCIÓN: Selección de parámetros'
            #StaticBox
        wx.StaticBox(pl_materiales, -1, 'Parámetros', (5, 240), size=(290, 205))
            #StaticText
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Densidad:',pos=(20, 270))
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Módulo de Young:',pos=(20, 300))
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Resistencia mecánica:',pos=(20, 330))
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Conductividad térmica:',pos=(20, 360))
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Coef. dilatación térmica:',pos=(20, 390))
        self.lb_ejey=wx.StaticText(pl_materiales, -1, 'Temp. máx. de servicio:',pos=(20, 420))
        wx.StaticText(pl_materiales, -1, 'min',pos=(155, 255))
        wx.StaticText(pl_materiales, -1, 'max',pos=(200, 255))
            #unidades
        wx.StaticText(pl_materiales, -1, '[kg/m^3]',pos=(235, 270))
        wx.StaticText(pl_materiales, -1, '[GPa]',pos=(235, 300))
        wx.StaticText(pl_materiales, -1, '[MPa]',pos=(235, 330))
        wx.StaticText(pl_materiales, -1, '[W/mK]',pos=(235, 360))
        wx.StaticText(pl_materiales, -1, '[10^-6/°C]',pos=(235, 390))
        wx.StaticText(pl_materiales, -1, '[°C]',pos=(235, 420))
            #TextBox
                #valores mínimos
        self.txt_densidad_min = wx.TextCtrl(pl_materiales, -1,pos=(150, 270),size=(40,20))
        self.txt_young_min = wx.TextCtrl(pl_materiales, -1,pos=(150, 300),size=(40,20))
        self.txt_rmecanica_min = wx.TextCtrl(pl_materiales, -1,pos=(150, 330),size=(40,20))
        self.txt_ctermica_min = wx.TextCtrl(pl_materiales, -1,pos=(150, 360),size=(40,20))
        self.txt_cdilatacion_min = wx.TextCtrl(pl_materiales, -1,pos=(150, 390),size=(40,20))
        self.txt_temp_serv_min = wx.TextCtrl(pl_materiales, -1,pos=(150, 420),size=(40,20))
                #valores máximos
        self.txt_densidad_max = wx.TextCtrl(pl_materiales, -1,pos=(195, 270),size=(40,20))
        self.txt_young_max = wx.TextCtrl(pl_materiales, -1,pos=(195, 300),size=(40,20))
        self.txt_rmecanica_max = wx.TextCtrl(pl_materiales, -1,pos=(195, 330),size=(40,20))
        self.txt_ctermica_max = wx.TextCtrl(pl_materiales, -1,pos=(195, 360),size=(40,20))
        self.txt_cdilatacion_max = wx.TextCtrl(pl_materiales, -1,pos=(195, 390),size=(40,20))
        self.txt_temp_serv_max = wx.TextCtrl(pl_materiales, -1,pos=(195, 420),size=(40,20))
        
        box_materiales=wx.BoxSizer(wx.VERTICAL)
        self.panel_controles.SetSizer(box_materiales)

        #   **SOBRE PANEL ARBOL DE MATERIALES**
        'SECCIÓN: árbol de materiales'
        self.tree= wx.TreeCtrl(pl_arbol, 1, wx.DefaultPosition, (295,180) , style=wx.TR_DEFAULT_STYLE)        
        
        #Ordena los paneles de opciones y materiales
        box_controles=wx.BoxSizer(wx.VERTICAL)
        box_controles.Add(pl_opciones,0,wx.EXPAND)
        box_controles.Add(pl_materiales,1,wx.EXPAND)
        box_controles.Add(pl_arbol,2,wx.EXPAND)
        
        self.panel_controles.SetSizer(box_controles)

        #===========CONDICIONES INICIALES DE LA INTERFAZ======================
        'SECCIÓN: Selección de familias'
        self.cb_todo.SetValue(True), self.cb_metales.SetValue(True)
        self.cb_ceramicos.SetValue(True)
        self.cb_compuestos.SetValue(True)
        self.cb_polimeros.SetValue(True)
        self.cb_elastomeros.SetValue(True)
        self.cb_espumas.SetValue(True)
        self.cb_naturales.SetValue(True)
        'SECCIÓN: Selección de propieadades'
        self.cmbo_prop_x.SetSelection(1)
        self.cmbo_prop_y.SetSelection(0)
        'SECCIÓN: Selección de índice'
        self.tb_indice.Enable(False)
        self.sc_indice.SetValue(1)
        self.cmbo_filtro.SetSelection(0)

        #===============PROGRAMACIÓN DE OBTJETOS====================
        'SECCIÓN: Botones de mando'
        #Botón GRAFICAR
        self.b_graficar.Bind(wx.EVT_BUTTON,self.Graficar)
        #Botón NOMBRES
        self.tb_nombres.Bind(wx.EVT_TOGGLEBUTTON,self.Mostrar_nombres)
        'SECCIÓN: Selección de familias'
            #CheckBox
        self.cb_todo.Bind(wx.EVT_CHECKBOX,self.check_all)
        self.cb_metales.Bind(wx.EVT_CHECKBOX,self.some_material)
        self.cb_ceramicos.Bind(wx.EVT_CHECKBOX,self.some_material)
        self.cb_compuestos.Bind(wx.EVT_CHECKBOX,self.some_material)
        self.cb_polimeros.Bind(wx.EVT_CHECKBOX,self.some_material)
        self.cb_elastomeros.Bind(wx.EVT_CHECKBOX,self.some_material)
        self.cb_espumas.Bind(wx.EVT_CHECKBOX,self.some_material)
        self.cb_naturales.Bind(wx.EVT_CHECKBOX,self.some_material)
        'SECCIÓN: árbol de materiales'
        #ÁRBOL DE MATERIALES
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED,self.Nombre_material)
        'SECCIÓN: Selección de índice'

    def Graficar_rectaIndice(self,event):
        'Grafica la recta del INDICE al hacer clic'
        if self.tb_indice.GetValue()==True:            
            if event.inaxes != self.ax.axes: return     

            xpos,ypos=event.xdata, event.ydata  # coordenadas del punto donde se hace click
            
            px=np.log10(xpos)   
            py=np.log10(ypos)
            
            self.m=self.sc_indice.GetValue() # valor de pendiente
            self.b=-self.m*px+py    
            
            #punto inicial al borde para graficar la recta
            yi_log=self.m*np.log10(self.xmin)+self.b
            yf_log=self.m*np.log10(self.xmax)+self.b
            
            yi=10**yi_log
            yf=10**yf_log

            'Se debe mantener el orden de las siguientes 5 líneas'
            self.Graficar(event)    #vuelve a graficar (para borrar la recta anterior)
            self.ax.autoscale(False)    #evita que la escala se distorsione
            self.ax.plot((self.xmin,self.xmax),(yi,yf),'-',color='black',lw=1)  #agrega la recta a la gráfica
            self.ax.grid(True)
            self.canvas.draw()      #muestra la gráfica

    def Nombre_material(self,event):
        'Muestra en la gráfica el nombre del material al hacer doble clic sobre su ítem en el árbol de materiales'
        item = self.tree.GetSelection()
        nombre=self.tree.GetItemText(item)
        #SELECCIÓN DE PROPIEDADES A GRAFICAR
        x_propiedad,y_propiedad,xlabel,ylabel=self.seleccion_propiedad()
        for i in range(len(self.LISTA)):    #i=lista de cada región'
            for j in range(len(self.LISTA[i])): #j=cantidad de materiales de cada region'
                if self.LISTA[i][j][4]==nombre:
                    posx=(float(self.LISTA[i][j][x_propiedad+5])+float(self.LISTA[i][j][x_propiedad+6]))/2
                    posy=(float(self.LISTA[i][j][y_propiedad+5])+float(self.LISTA[i][j][y_propiedad+6]))/2

                    self.ax.annotate(nombre, xy=(posx,posy),xytext=(posx+20,posy+20),bbox={'facecolor':'yellow', 'alpha':1, 'pad':2},
                                     arrowprops=dict(arrowstyle="->"))                    
        self.canvas.draw()

    def Mostrar_nombres(self,event):
        'Muestra en la gráfica los nombres de todos los materiales visualizados'
        if self.tb_nombres.GetValue()==True:
            for i in range(len(self.LISTA_VALIDADA)):    #i=lista de cada región'
                if self.LISTA_VALIDADA[i]!=[]:
                    for j in range(len(self.LISTA_VALIDADA[i])): #j=cantidad de materiales de cada region'
                        nombre=self.LISTA_VALIDADA[i][j][4]
                        #SELECCIÓN DE PROPIEDADES A GRAFICAR
                        x_propiedad,y_propiedad,xlabel,ylabel=self.seleccion_propiedad()

                        posx=(float(self.LISTA_VALIDADA[i][j][x_propiedad+5])+float(self.LISTA_VALIDADA[i][j][x_propiedad+6]))/2
                        posy=(float(self.LISTA_VALIDADA[i][j][y_propiedad+5])+float(self.LISTA_VALIDADA[i][j][y_propiedad+6]))/2

                        self.ax.text(posx,posy,nombre,fontsize=8,bbox={'facecolor':'yellow', 'alpha':1, 'pad':2})
            self.canvas.draw()
        else:
            self.Graficar(event)

    def seleccion_propiedad(self):
        'Selecciona desde la base la propiedad a graficar en x e y'
        #Propiedad en x
        if self.cmbo_prop_x.GetValue()=='Módulo de young':
            x_propiedad=2
            xlabel=r"Módulo de Young, E [GPa]"
        elif self.cmbo_prop_x.GetValue()=='Densidad':
            x_propiedad=0
            xlabel=r"Densidad, $\rho$ [kg/m$^3$]"
        elif self.cmbo_prop_x.GetValue()=='Resistencia mecánica':
            x_propiedad=4
            xlabel='Resistencia mecánica, [MPa]'
        elif self.cmbo_prop_x.GetValue()=='Conductividad térmica':
            x_propiedad=6
            xlabel='Resistencia térmica, [W/mK]'
        elif self.cmbo_prop_x.GetValue()=='Coef. dilatación térmica':
            x_propiedad=8
            xlabel='Coeficiente de dilatación, [10$^-$$^6$/°C]'
        elif self.cmbo_prop_x.GetValue()=='Temp. máx. de servicio':
            x_propiedad=10
            xlabel='Temperatura máxima de servicio, [°C]'

        #Propiedad en y
        if self.cmbo_prop_y.GetValue()=='Módulo de young':
            y_propiedad=2
            ylabel=r"Módulo de Young, E [GPa]"
        elif self.cmbo_prop_y.GetValue()=='Densidad':
            y_propiedad=0
            ylabel=r"Densidad, $\rho$ [kg/m$^3$]"
        elif self.cmbo_prop_y.GetValue()=='Resistencia mecánica':
            y_propiedad=4
            ylabel='Resistencia mecánica, [MPa]'
        elif self.cmbo_prop_y.GetValue()=='Conductividad térmica':
            y_propiedad=6
            ylabel='Resistencia térmica, [W/mK]'
        elif self.cmbo_prop_y.GetValue()=='Coef. dilatación térmica':
            y_propiedad=8
            ylabel='Coeficiente de dilatación, [10$^-$$^6$/°C]'
        elif self.cmbo_prop_y.GetValue()=='Temp. máx. de servicio':
            y_propiedad=10
            ylabel='Temperatura máxima de servicio, [°C]'

        return x_propiedad,y_propiedad,xlabel,ylabel

    def Graficar(self,event):
        'Grafica los diagramas de Ashby'
        self.ax.cla()   #Limpia el área del gráfico
        self.tree.DeleteAllItems()  #Limpia los ítems en el arbol de materiales
        self.tb_indice.Enable(True)

        #SELECCIÓN DE PROPIEDADES A GRAFICAR
        x_propiedad,y_propiedad,xlabel,ylabel=self.seleccion_propiedad()

        #LLAMA a la función de VALIDACIÓN DE PARÁMETROS para graficar de acuerdo a los parámetros definidos por el usuario
        self.R1,self.R2,self.R3,self.R4,self.R5,self.R6,self.R7,self.LISTA=self.validacion_parametros()

        #Árbol de materiales'
        root = self.tree.AddRoot('Regiones')

        self.LISTA_VALIDADA=[]
        #============Condicionales para graficar RANGOS, REGIONES y RECTA DEL ÍNDICE===========================
        if self.cb_metales.GetValue()==True:
            color='red'
            if len(self.R5)!=0:
                R5_pts=self.rango_materiales(self.R5,x_propiedad,y_propiedad,color)     #metales
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R5_pts,color)

                if self.tb_indice.GetValue()==True and self.clic=="in":
                    print ('dentro de in')
##                    if self.clic=="in":
                    n=int(len(R5_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_metales=[]
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R5_pts[pos,1])
                        lim_sup_y=np.log10(R5_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R5_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R5_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_metales.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_metales.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_metales.append(pos)

                    R5_pts=R5_pts[i_metales, :]
                    
                    Lista_R5=[]
                    for i in range(len(i_metales)):
                        Lista_R5.append(self.LISTA[4][int(i_metales[i]/8)])
                else:
                    R5_pts=self.R5
                    Lista_R5=self.LISTA[4]
                
                self.LISTA_VALIDADA.append(Lista_R5)                

                if Lista_R5!=[]:    #solo si existe materiales en la lista agrego la categoría al árbol de materiales
                    #Agrego los nombres de materiales al arbol visual  
                    R_metales=self.tree.AppendItem(root, 'Región Metales')
                    for i in range(len(R5_pts)):
                        if Lista_R5[i][3]=='Ferrosos':
                            ferrosos=self.tree.AppendItem(R_metales,'Ferrosos')
                            break
                            
                    for i in range(len(R5_pts)):
                        if Lista_R5[i][3]=='No ferrosos':
                            no_ferrosos=self.tree.AppendItem(R_metales,'No ferrosos')
                            break
                            
                    for i in range(len(R5_pts)):
                        if Lista_R5[i][3]=='Ferrosos':
                            self.tree.AppendItem(ferrosos,Lista_R5[i][4])
                        else:
                            self.tree.AppendItem(no_ferrosos,Lista_R5[i][4])
                            
        if self.cb_ceramicos.GetValue()==True:
            color='yellow'
            if len(self.R1)!=0:
                R1_pts=self.rango_materiales(self.R1,x_propiedad,y_propiedad,color)     #ceramicos
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R1_pts,color)

                if self.tb_indice.GetValue()==True and self.clic=="in":
                    n=int(len(R1_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_ceramicos=[]     #
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R1_pts[pos,1])
                        lim_sup_y=np.log10(R1_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R1_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R1_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_ceramicos.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_ceramicos.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_ceramicos.append(pos)

                    R1_pts=R1_pts[i_ceramicos, :]
                    
                    Lista_R1=[]
                    for i in range(len(i_ceramicos)):
                        Lista_R1.append(self.LISTA[0][int(i_ceramicos[i]/8)])
                else:
                    R1_pts=self.R1
                    Lista_R1=self.LISTA[0]
                    
                self.LISTA_VALIDADA.append(Lista_R1)
                
                if Lista_R1!=[]:
                    R_ceramicos=self.tree.AppendItem(root, 'Región Cerámicos')
                    for i in range(len(R1_pts)):
                        self.tree.AppendItem(R_ceramicos,Lista_R1[i][4])
                    
        if self.cb_compuestos.GetValue()==True:
            color='brown'      #corregir color
            if len(self.R2)!=0:
                R2_pts=self.rango_materiales(self.R2,x_propiedad,y_propiedad,color)     #compuestos
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R2_pts,color)

                if self.tb_indice.GetValue()==True and self.clic=="in":
                    n=int(len(R2_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_compuestos=[]     #
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R2_pts[pos,1])
                        lim_sup_y=np.log10(R2_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R2_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R2_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_compuestos.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_compuestos.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_compuestos.append(pos)

                    R2_pts=R2_pts[i_compuestos, :]
                    
                    Lista_R2=[]
                    for i in range(len(i_compuestos)):
                        Lista_R2.append(self.LISTA[1][int(i_compuestos[i]/8)])
                else:
                    R2_pts=self.R2
                    Lista_R2=self.LISTA[1]

                self.LISTA_VALIDADA.append(Lista_R2)

                if Lista_R2!=[]:
                    R_compuestos=self.tree.AppendItem(root, 'Región Compuestos')
                    comp_hibridos=self.tree.AppendItem(R_compuestos, 'Híbridos')
                    for i in range(len(R2_pts)):
                        self.tree.AppendItem(comp_hibridos,Lista_R2[i][4])

        if self.cb_espumas.GetValue()==True:
            color='green'
            if len(self.R4)!=0:
                R4_pts=self.rango_materiales(self.R4,x_propiedad,y_propiedad,color)     #espumas
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R4_pts,color)

                if self.tb_indice.GetValue()==True and self.clic=="in":
                    n=int(len(R4_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_espumas=[]     #
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R4_pts[pos,1])
                        lim_sup_y=np.log10(R4_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R4_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R4_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_espumas.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_espumas.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_espumas.append(pos)

                    R4_pts=R4_pts[i_espumas, :]
                    
                    Lista_R4=[]
                    for i in range(len(i_espumas)):
                        Lista_R4.append(self.LISTA[3][int(i_espumas[i]/8)])
                else:
                    R4_pts=self.R4
                    Lista_R4=self.LISTA[3]

                self.LISTA_VALIDADA.append(Lista_R4)

                if Lista_R4!=[]:
                    R_espumas=self.tree.AppendItem(root, 'Región Espumas')
                    espuma_hibridos=self.tree.AppendItem(R_espumas, 'Híbridos')
                    for i in range(len(R4_pts)):
                        self.tree.AppendItem(espuma_hibridos,Lista_R4[i][4])                

        if self.cb_naturales.GetValue()==True:
            color='DimGrey'     #corregir color
            if len(self.R6)!=0:
                R6_pts=self.rango_materiales(self.R6,x_propiedad,y_propiedad,color)     #naturales
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R6_pts,color)
                    
                if self.tb_indice.GetValue()==True and self.clic=="in":
                    n=int(len(R6_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_naturales=[]     #
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R6_pts[pos,1])
                        lim_sup_y=np.log10(R6_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R6_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R6_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_naturales.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_naturales.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_naturales.append(pos)

                    R6_pts=R6_pts[i_naturales, :]
                    
                    Lista_R6=[]
                    for i in range(len(i_naturales)):
                        Lista_R6.append(self.LISTA[5][int(i_naturales[i]/8)])
                else:
                    R6_pts=self.R6
                    Lista_R6=self.LISTA[5]

                self.LISTA_VALIDADA.append(Lista_R6)

                if Lista_R6!=[]:    #solo si existe materiales en la lista agrego la categoría al árbol de materiales
                    R_naturales=self.tree.AppendItem(root, 'Región Naturales')
                    natural_hibridos=self.tree.AppendItem(R_naturales, 'Híbridos')
                    for i in range(len(R6_pts)):
                        self.tree.AppendItem(natural_hibridos,Lista_R6[i][4])

        if self.cb_elastomeros.GetValue()==True:
            color='cyan'
            if len(self.R3)!=0:
                R3_pts=self.rango_materiales(self.R3,x_propiedad,y_propiedad,color)     #elastomeros
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R3_pts,color)

                if self.tb_indice.GetValue()==True and self.clic=="in":
                    n=int(len(R3_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_elastomeros=[]     #
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R3_pts[pos,1])
                        lim_sup_y=np.log10(R3_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R3_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R3_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_elastomeros.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_elastomeros.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_elastomeros.append(pos)

                    R3_pts=R3_pts[i_elastomeros, :]
                    
                    Lista_R3=[]
                    for i in range(len(i_elastomeros)):
                        Lista_R3.append(self.LISTA[2][int(i_elastomeros[i]/8)])
                else:
                    R3_pts=self.R3
                    Lista_R3=self.LISTA[2]

                self.LISTA_VALIDADA.append(Lista_R3)

                if Lista_R3!=[]:
                    R_elastomeros=self.tree.AppendItem(root, 'Región Elastómeros')
                    for i in range(len(R3_pts)):
                        self.tree.AppendItem(R_elastomeros,Lista_R3[i][4])

        if self.cb_polimeros.GetValue()==True:
            color='blue'
            if len(self.R7)!=0:
                R7_pts=self.rango_materiales(self.R7,x_propiedad,y_propiedad,color)     #polimeros
                if self.tb_regiones.GetValue()==True:
                    self.grafico_regiones(R7_pts,color)

                if self.tb_indice.GetValue()==True and self.clic=="in":
                    n=int(len(R7_pts)/8)     #cantidad de materiales en la región (cada materiale tiene 8 puntos)
                    i_polimeros=[]     #
                    for i in range(n):
                        pos=i*8

                        'rango en eje y'
                        lim_inf_y=np.log10(R7_pts[pos,1])
                        lim_sup_y=np.log10(R7_pts[pos+4,1])

                        b_sup=lim_sup_y-self.m*np.log10(R7_pts[pos+6,0])    #corte en eje y en la esquina superior izquierda del rectángulo del rango
                        b_inf=lim_inf_y-self.m*np.log10(R7_pts[pos+2,0])    #corte en eje y en la esquina inferior derecha del rectángulo del rango

                        #filtro de materiales dependiendo el filtro superior, inferior o sobre línea
                        if self.cmbo_filtro.GetValue()=='Superior':
                            if self.b<=b_sup:
                                i_polimeros.append(pos)
                        elif self.cmbo_filtro.GetValue()=='Sobre línea':
                            if self.b<=b_sup and self.b>=b_inf:   #si b de la recta del indice está entre el b_sup e inf entonces la recta pasa a traves del rango del material
                                i_polimeros.append(pos)    #lista con las posiciones del material en la matriz de la region de materiales
                        elif self.cmbo_filtro.GetValue()=='Inferior':
                            if self.b>=b_sup:
                                i_polimeros.append(pos)

                    R7_pts=R7_pts[i_polimeros, :]
                    
                    Lista_R7=[]
                    for i in range(len(i_polimeros)):
                        Lista_R7.append(self.LISTA[6][int(i_polimeros[i]/8)])
                else:
                    R7_pts=self.R7
                    Lista_R7=self.LISTA[6]

                self.LISTA_VALIDADA.append(Lista_R7)

                if Lista_R7!=[]:
                    R_polimeros=self.tree.AppendItem(root, 'Región Polímeros')
                    for i in range(len(R7_pts)):
                        if Lista_R7[i][3]=='Termoestables':
                            termoestables=self.tree.AppendItem(R_polimeros,'Termoestables')
                            break
                            
                    for i in range(len(R7_pts)):
                        if Lista_R7[i][3]=='Termoplasticos':
                            termoplasticos=self.tree.AppendItem(R_polimeros,'Termoplasticos')
                            break
                            
                    for i in range(len(R7_pts)):
                        if Lista_R7[i][3]=='Termoestables':
                            self.tree.AppendItem(termoestables,Lista_R7[i][4])
                        else:
                            self.tree.AppendItem(termoplasticos,Lista_R7[i][4])
                            
        if self.tb_nombres.GetValue()==True:
            for i in range(len(self.LISTA_VALIDADA)):    #i=lista de cada región'
                if self.LISTA_VALIDADA[i]!=[]:
                    for j in range(len(self.LISTA_VALIDADA[i])): #j=cantidad de materiales de cada region'
                        nombre=self.LISTA_VALIDADA[i][j][4]
                        #SELECCIÓN DE PROPIEDADES A GRAFICAR
                        x_propiedad,y_propiedad,xlabel,ylabel=self.seleccion_propiedad()

                        posx=(float(self.LISTA_VALIDADA[i][j][x_propiedad+5])+float(self.LISTA_VALIDADA[i][j][x_propiedad+6]))/2
                        posy=(float(self.LISTA_VALIDADA[i][j][y_propiedad+5])+float(self.LISTA_VALIDADA[i][j][y_propiedad+6]))/2

                        self.ax.text(posx,posy,nombre,fontsize=8,bbox={'facecolor':'yellow', 'alpha':1, 'pad':2})
            
        self.tree.Expand(root)   #expande la lista de regiones de materiales disponibles
        
        self.ax.semilogx()
        self.ax.semilogy()
        self.ax.autoscale(True)
        self.ax.grid(True)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.canvas.draw()  #grafica lo seleccionado
        self.xmin,self.xmax,self.ymin,self.ymax=self.ax.axis()
          
    def check_all(self, event):
        'Selecciona o deselecciona todos los CheckBoxs si "Graficar todo" cambia de estado'
        if self.cb_todo.GetValue():
            self.cb_metales.SetValue(True)
            self.cb_ceramicos.SetValue(True)
            self.cb_compuestos.SetValue(True)
            self.cb_polimeros.SetValue(True)
            self.cb_elastomeros.SetValue(True)
            self.cb_espumas.SetValue(True)
            self.cb_naturales.SetValue(True)
        else:
            self.cb_metales.SetValue(False)
            self.cb_ceramicos.SetValue(False)
            self.cb_compuestos.SetValue(False)
            self.cb_polimeros.SetValue(False)
            self.cb_elastomeros.SetValue(False)
            self.cb_espumas.SetValue(False)
            self.cb_naturales.SetValue(False)
            
    def some_material(self, event):
        'Cambia el estado del CheckBox "Graficar todo"'
        if self.cb_metales.GetValue()==False:
            self.cb_todo.SetValue(False)
        elif self.cb_ceramicos.GetValue()==False:
            self.cb_todo.SetValue(False)
        elif self.cb_compuestos.GetValue()==False:
            self.cb_todo.SetValue(False)
        elif self.cb_polimeros.GetValue()==False:
            self.cb_todo.SetValue(False)
        elif self.cb_elastomeros.GetValue()==False:
            self.cb_todo.SetValue(False)
        elif self.cb_espumas.GetValue()==False:
            self.cb_todo.SetValue(False)
        elif self.cb_naturales.GetValue()==False:
            self.cb_todo.SetValue(False)

        if self.cb_metales.GetValue()==True:
            if self.cb_ceramicos.GetValue()==True:
                if self.cb_compuestos.GetValue()==True:
                    if self.cb_polimeros.GetValue()==True:
                        if self.cb_elastomeros.GetValue()==True:
                            if self.cb_espumas.GetValue()==True:
                                if self.cb_naturales.GetValue()==True:
                                    self.cb_todo.SetValue(True)        
                
    def rango_materiales(self,R,x_propiedad,y_propiedad,color_rango):
        'grafica las elipses que representan los rangos de las propiedades de cada material'

        'aquí ingresa la familia o subfamilia con maximos y minimos para ser graficados'

        color=color_rango
        datos_x=R[:,x_propiedad:x_propiedad+2]
        datos_y=R[:,y_propiedad:y_propiedad+2]

        pts_region=[]
        for i in range(len(R)):
            mx=(datos_x[i,0]+datos_x[i,1])/2
            my=(datos_y[i,0]+datos_y[i,1])/2
            if mx!=0 and my!=0:
                ancho=datos_x[i,1]-datos_x[i,0]
                alto=datos_y[i,1]-datos_y[i,0]

                'Se obtiene una matriz: pts_rango[fila]=[abajo, derecha, arriba, izquierda]'
                p2=(np.log10(mx+ancho/2), np.log10(my-alto/2))
                p4=(np.log10(mx+ancho/2), np.log10(my+alto/2))
                p6=(np.log10(mx-ancho/2), np.log10(my+alto/2))
                p8=(np.log10(mx-ancho/2), np.log10(my-alto/2))
                'Vértices del rectángulo que contiene la elipse (rango)'
                p1=((p4[0]+p6[0])/2,p2[1])
                p3=(p2[0],(p2[1]+p4[1])/2)
                p5=(p1[0],p4[1])
                p7=(p6[0],p3[1])
                '8 puntos necesarios para dibujar la elipse'
                p1=[10**p1[0],10**p1[1]]
                p2=[10**p2[0],10**p2[1]]
                p3=[10**p3[0],10**p3[1]]
                p4=[10**p4[0],10**p4[1]]
                p5=[10**p5[0],10**p5[1]]
                p6=[10**p6[0],10**p6[1]]
                p7=[10**p7[0],10**p7[1]]
                p8=[10**p8[0],10**p8[1]]
                'agrega los puntos en una misma tupla'
                pts_region.append(p1)
                pts_region.append(p2)
                pts_region.append(p3)
                pts_region.append(p4)
                pts_region.append(p5)
                pts_region.append(p6)
                pts_region.append(p7)
                pts_region.append(p8)
                
                pts_ovalo=[p1,p2,p3,p4,p5,p6,p7,p8,p1]

                codes_ovalo = [Path.MOVETO,
                               Path.CURVE3,
                               Path.CURVE3,
                               Path.CURVE3,
                               Path.CURVE3,
                               Path.CURVE3,
                               Path.CURVE3,
                               Path.CURVE3,
                               Path.CURVE3]
                
                path = Path(pts_ovalo, codes_ovalo)
                patch = patches.PathPatch(path, facecolor=color, lw=0.5, alpha=0.8)
                self.ax.add_patch(patch)

        'Convierte la tupla de puntos en una matriz'
        pts_rango=np.zeros((len(pts_region),2))
        for i in range(len(pts_region)):
            pts_rango[i,:]=[pts_region[i][0],pts_region[i][1]]
           
        return pts_rango
        'retorna una matriz con las coordenadas (x,y) de los puntos extremos(abajo, derec,arriba,izq)...'
        '...de la elipse(rango) de cada material de la región'

    def contorno(self,pts):
        'dibuja un arco que cubre el punto 2'   
        def ptos_paralelos(p1,p2):
            'encuentra la pendiente entre dos puntos'
            'p1=(x1,y1); p2=(x2,y2)'
##            cd=0.1034 distancia inicial
            cd=0.035    #distancia paralela a cada lado

            p1xlog=np.log10(p1[0])
            p1ylog=np.log10(p1[1])
            p2xlog=np.log10(p2[0])
            p2ylog=np.log10(p2[1])

            if p2xlog-p1xlog==0:    #evito el error de tan(90°)
                m=9999999999
            else:
                m=(p2ylog-p1ylog)/(p2xlog-p1xlog)
                teta=np.arctan(m)

            if m==0:    #evito el error de división para cero al calcular la pendiente perpendicular
                m=0.0000001
            
            m_p=-1/m #pendiente perpendicular
            teta_p=np.arctan(m_p)

            x_mediolog=(p1xlog+p2xlog)/2
            y_mediolog=(p1ylog+p2ylog)/2

            x_mp=10**x_mediolog
            y_mp=10**y_mediolog
##            self.ax.plot(x_mp, y_mp,'ko',color='blue',markersize=5)
            
            dx=abs(cd*np.cos(teta_p))
            dy=abs(cd*np.sin(teta_p))

            #condicionales para identificar en que dirección ubicar el punto
            # de la recta paralela (arriba o abajo del lado)

            if p2xlog>p1xlog:
                if p2ylog>p1ylog:
                    px=x_mediolog+dx
                    py=y_mediolog-dy
                elif p2ylog<p1ylog:
                    px=x_mediolog-dx
                    py=y_mediolog-dy
                elif p2ylog==p1ylog:
                    px=x_mediolog
                    py=y_mediolog-cd
            elif p2xlog<p1xlog:
                if p2ylog>p1ylog:
                    px=x_mediolog+dx
                    py=y_mediolog+dy
                elif p2ylog<p1ylog:
                    px=x_mediolog-dx
                    py=y_mediolog+dy
                elif p2ylog==p1ylog:
                    px=x_mediolog
                    py=y_mediolog+cd
            elif p2xlog==p1xlog:
                if p2ylog>p1ylog:
                    px=x_mediolog+dx
                    py=y_mediolog
                elif p2ylog<p1ylog:
                    px=x_mediolog-dx
                    py=y_mediolog

            pto_paralelo=np.array([px,py])

            return pto_paralelo,m   #coordenadas del punto de referencia de la recta paralela
            'pto_paralelo=(px,py) coordenadas del punto para construir la recta paralela'
            'm=pendiente de la recta'

        #Sentencia para ubicar el punto para la paralela del lado
        coordenadas_m=[]
        for i in range(2):
            coordenadas_m.append(ptos_paralelos(pts[i],pts[i+1]))
        'coordenadas_m=[[[px1,py1],m1] , [[px2,py2],m2]]'
        
        'descomposición del arreglo de "coordenadas"'
        pc1=coordenadas_m[0][0]
        pc2=coordenadas_m[1][0]
        m1=coordenadas_m[0][1]
        m2=coordenadas_m[1][1]
        'coordenadas de punto paralelo'
        px1=pc1[0]
        py1=pc1[1]
        px2=pc2[0]
        py2=pc2[1]
        'vértices para formar el arco'
        vx=((py2-m2*px2)-(py1-m1*px1))/(m1-m2)
        vy=m1*vx-m1*px1+py1
        
        vx=10**vx
        vy=10**vy

        px1=10**px1
        py1=10**py1
        px2=10**px2
        py2=10**py2

        p1=np.array([px1,py1])
        p2=np.array([px2,py2])
        v=np.array([vx,vy])

        return v,p2  #los 3 puntos para formar el arco en cada vertice del poligono

    def grafico_regiones(self, region, color_region):
        'Extrae los puntos de borde para graficar las regiones'
        points = region
        points=np.log10(points) #escala logarítmica
        
        color=color_region
        #FUNCIÓN PRINCIPAL
        hull=ConvexHull(points)
        hull_indices=np.unique(hull.simplices.flat) #indices de los pares ordenados que forman el borde
        hull_points = points[hull_indices, :] #extrae los pares ordenados guiados por hull_indices
        
        #hull_points: PUNTOS DE BORDE desordenados
        ymin=np.argmin(points[:,1])   #mínimo valor en y
        pmin=points[ymin,:] #coordenadas con el mínimo valor en y

        points_order=[] #PUNTOS DE BORDE ordenados respecto a la coordenada y menor
        for i in range(0,len(hull_points)):
            points_order.append(hull_points[i])

        points_order.sort(key=lambda p: np.arctan2(p[1]-pmin[1],p[0]-pmin[0]))
        points_order=np.array(points_order)

        points_order=10**points_order   #ESCALA NORMAL

        n=len(points_order) #número de vertices del polígono o número de puntos de borde

        pts_borde=np.zeros(((2*n)+1,2))
        indice=1   #indice de ubicación para la matriz de pts_borde
        
        for i in range(len(points_order)):
            pt1=points_order[i]   #punto de referencia para iniciar el trazado: linea-arco
            if i==(len(points_order)-2):    #i= última coordenada de points_order
                pt2=points_order[i+1]  #next_point es el punto inicial
                pt3=points_order[0]
            elif i==(len(points_order)-1):
                pt2=points_order[0]   #el siguiente punto es en sentido horario debido al ordenamiento de points_order
                pt3=points_order[1]
            else:
                pt2=points_order[i+1]   
                pt3=points_order[i+2]
            
            pts=np.zeros((3,2)) #matriz con las coordenadas de 3 puntos continuos
            pts[0]=pt1
            pts[1]=pt2
            pts[2]=pt3
            v,p2=self.contorno(pts)
            
            pts_borde[indice]=v
            pts_borde[indice+1]=p2

            indice=indice+2

        pts_codes=[]
        pts_codes.append(Path.MOVETO)
        for i in range(1,len(pts_borde)):
            pts_codes.append(Path.CURVE3)

        'grafica las regiones'
        pts_borde[0]=pts_borde[1]   #agrego el punto inicial "MOVETO" a la matriz de puntos de borde

        path = Path(pts_borde, pts_codes)
        patch = patches.PathPatch(path, facecolor=color, lw=0, alpha=0.3)
        self.ax.add_patch(patch)
        
        'grafica los bordes de las regiones'
        pts_borde[0]=pts_borde[len(pts_borde)-1]   #agrega el punto inicial "MOVETO" a la matriz de puntos de borde

        path = Path(pts_borde, pts_codes)
        edge = patches.PathPatch(path, edgecolor='grey', facecolor='none', lw=1)
        self.ax.add_patch(edge)

    def importacion_datos(self):
        'importa los datos desde las BASE DE MATERIALES'
        'y entrega una matriz con los valores de las 7 regiones de ASHBY'
        archivo_base_excel=xl.open_workbook('Base Materiales TESIS.xlsx')
        hoja_base=archivo_base_excel.sheet_by_name('Hoja1')
        total_filas=hoja_base.nrows #total filas con datos
        total_colums=hoja_base.ncols    #total columnas con datos

        tabla=[]    #tabla de Base de Materiales importada de EXCEL 
        fila=[]
        for i in range(1,total_filas):
            for j in range (total_colums):
                fila.append(hoja_base.cell(i,j).value)
            tabla.append(fila)
            fila=[]
            i=i+1
        return tabla
            
    def validacion_parametros(self):
        'Selecciona los materiales de cada familia que cumplen los parámetros definidos por el usuario'

        #PARÁMETROS PARA FILTRAR MATERIALES
        'obtención de parámetros mínimos'
        densidad_min = self.txt_densidad_min.GetValue()
        young_min = self.txt_young_min.GetValue()
        rmecanica_min = self.txt_rmecanica_min.GetValue()
        ctermica_min = self.txt_ctermica_min.GetValue()
        cdilatacion_min = self.txt_cdilatacion_min.GetValue()
        temp_serv_min = self.txt_temp_serv_min.GetValue()
        'obtención de parámetros máximos'
        densidad_max = self.txt_densidad_max.GetValue()
        young_max = self.txt_young_max.GetValue()
        rmecanica_max = self.txt_rmecanica_max.GetValue()
        ctermica_max = self.txt_ctermica_max.GetValue()
        cdilatacion_max = self.txt_cdilatacion_max.GetValue()
        temp_serv_max = self.txt_temp_serv_max.GetValue()

        tabla=self.tabla    #agrego la tabla de datos importados a una variable interna
        #obtengo la lista de familias y subfamilias de la tabla
        regiones=list()
        familias=list()
        subfamilias=list()
        for i in range(len(tabla)):
            regiones.append(tabla[i][1])
            familias.append(tabla[i][2])
            subfamilias.append(tabla[i][3])
            
        nom_regiones=list(set(regiones))    #lista de regiones sin duplicados
        nom_regiones.sort()     #orden alfabético
        nom_familias=list(set(familias))    #lista de familias sin duplicados
        nom_familias.sort()  #orden alfabético
        nom_subfamilias=list(set(subfamilias))    #lista de subfamilias sin duplicados
        nom_subfamilias.sort()  #orden alfabético 
        #ceramicos,compuestos,elastomeros,espumas,metales,naturales,no tecnicos,polimeros
        tabla_validada=[]    #tabla con los datos que cumplen cada parámetro dado
        if tabla!=[]:   #tabla inicial debe tener datos
            if densidad_min !=  '': #condicional cuando existe parámetro de densidad mínima
                for j in range(len(tabla)):
                    if float(tabla[j][6])>=float(densidad_min):    #Si la densidad del material(tabla[j][5]) es mayor que densida_min
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if densidad_max !=  '': #condicional cuando existe parámetro de densidad máxima
            if tabla!=[]:   #la nueva tabla debe contener datos aun para filtrar
                for j in range(len(tabla)):
                    if float(tabla[j][5])<=float(densidad_max):    #Si la densidad del material(tabla[j][5]) es mayor que densida_max
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if young_min !=  '': #condicional cuando existe parámetro de densidad máxima
            if tabla!=[]:   #la nueva tabla debe contener datos aun para filtrar
                for j in range(len(tabla)):
                    if float(tabla[j][8])>=float(young_min):    
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if young_max !=  '':
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][7])<=float(young_max):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]
        
        if rmecanica_min !=  '':
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][10])>=float(rmecanica_min):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if rmecanica_max !=  '':
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][9])<=float(rmecanica_max):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if ctermica_min !=  '': 
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][12])>=float(ctermica_min):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if ctermica_max !=  '':
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][11])<=float(ctermica_max):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]
        
        if cdilatacion_min !=  '':
            if tabla!=[]:
                for j in range(len(tabla)): 
                    if float(tabla[j][14])>=float(cdilatacion_min):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]
       
        if cdilatacion_max !=  '':
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][13])<=float(cdilatacion_max):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if temp_serv_min !=  '':
            if tabla!=[]:
                for j in range(len(tabla)): 
                    if float(tabla[j][16])>=float(temp_serv_min):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        if temp_serv_max !=  '':
            if tabla!=[]:
                for j in range(len(tabla)):
                    if float(tabla[j][15])<=float(temp_serv_max):
                        tabla_validada.append(tabla[j][0:17])
                tabla=tabla_validada
                tabla_validada=[]

        'HASTA AQUÍ SE TIENE LA TABLA CON DATOS FILTRADOS SEGÚN LOS PARÁMETROS DEFINIDOS POR EL USUARIO'
        LISTA_REGIONES=[] #lista que contiene las tablas de cada familia (sólo valores)
        tabla_region=[]    #lista que contiene la tabla de una familia
        for i in range(len(nom_regiones)):
            for j in range(len(tabla)):
                    if tabla[j][1]==nom_regiones[i]:
                            tabla_region.append(tabla[j][:])  #divido la tabla por regiones
            LISTA_REGIONES.append(tabla_region)  #agrego la tabla de la familia al diccionario
            tabla_region=[]

##        #Extraigo listas con los nombres de cada REGIÓN
##        R1_nombre=NOMBRE_REGIONES[0]    #CERÁMICOS
##        R2_nombre=NOMBRE_REGIONES[1]    #COMPUESTOS
##        R3_nombre=NOMBRE_REGIONES[2]    #ELASTOMEROS
##        R4_nombre=NOMBRE_REGIONES[3]    #ESPUMAS
##        R5_nombre=NOMBRE_REGIONES[4]    #METALES
##        R6_nombre=NOMBRE_REGIONES[5]    #NATURALES
##        R7_nombre=NOMBRE_REGIONES[7]    #POLÍMEROS
##        R8_nombre=NOMBRE_REGIONES[6]    #NO TÉCNICOS

        #Convierto cada región de tipo "lista" a "matriz"(permite hacer los cálculos)        
        R1=np.zeros((len(LISTA_REGIONES[0]),12))    #CERÁMICOS
        for i in range(len(LISTA_REGIONES[0])): #filas
            for j in range(5,len(LISTA_REGIONES[0][0])-1):  #columnas
                r=j-5
                R1[i,r]=float(LISTA_REGIONES[0][i][j])

        R2=np.zeros((len(LISTA_REGIONES[1]),12))    #COMPUESTOS
        for i in range(len(LISTA_REGIONES[1])): #filas
            for j in range(5,len(LISTA_REGIONES[1][0])-1):  #columnas
                r=j-5
                R2[i,r]=float(LISTA_REGIONES[1][i][j])

        R3=np.zeros((len(LISTA_REGIONES[2]),12))    #ELASTOMEROS
        for i in range(len(LISTA_REGIONES[2])): #filas
            for j in range(5,len(LISTA_REGIONES[2][0])-1):  #columnas
                r=j-5
                R3[i,r]=float(LISTA_REGIONES[2][i][j])

        R4=np.zeros((len(LISTA_REGIONES[3]),12))    #ESPUMAS
        for i in range(len(LISTA_REGIONES[3])): #filas
            for j in range(5,len(LISTA_REGIONES[3][0])-1):  #columnas
                r=j-5
                R4[i,r]=float(LISTA_REGIONES[3][i][j])

        R5=np.zeros((len(LISTA_REGIONES[4]),12))    #METALES
        for i in range(len(LISTA_REGIONES[4])): #filas
            for j in range(5,len(LISTA_REGIONES[4][0])-1):  #columnas
                r=j-5
                R5[i,r]=float(LISTA_REGIONES[4][i][j])

        R6=np.zeros((len(LISTA_REGIONES[5]),12))    #NATURALES
        for i in range(len(LISTA_REGIONES[5])): #filas
            for j in range(5,len(LISTA_REGIONES[5][0])-1):  #columnas
                r=j-5
                R6[i,r]=float(LISTA_REGIONES[5][i][j])

        R7=np.zeros((len(LISTA_REGIONES[6]),12))    #POLÍMEROS
        for i in range(len(LISTA_REGIONES[6])): #filas
            for j in range(5,len(LISTA_REGIONES[6][0])-1):  #columnas
                r=j-5
                R7[i,r]=float(LISTA_REGIONES[6][i][j])

        return R1,R2,R3,R4,R5,R6,R7,LISTA_REGIONES

if __name__ == '__main__':
    app = wx.App()
    GUI_ASHBY(None, title='GRÁFICAS ASHBY - FACULTAD DE INGENIERÍA MECÁNICA EPN')
    app.MainLoop()