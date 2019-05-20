import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import matplotlib
# this line needed to stop it crashing when using in tkinter
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import gridspec
from numpy.polynomial.polynomial import polyfit
import numpy as np

ALL = 'All'

class GraphGUI:

    UNIT, ACTIVITY, PERIOD, WORKOUT_AGGREGATOR = 'unit', 'activity', 'period', 'workout_aggregator'
    PERIOD_AGGREGATOR, ACTIVITY_TYPE, EQUIPMENT = 'period_aggregator', 'activity_type', 'equipment'
    DAY_TYPE, SLEEP_QUALITY, DAY, MONTH, GRAPH = 'day_type', 'sleep_quality', 'day_of_week', 'month', 'Graph'
    MENUS = [(UNIT, 2, 0), (ACTIVITY, 3, 0), (PERIOD, 4, 0), (WORKOUT_AGGREGATOR, 5, 0),
             (PERIOD_AGGREGATOR, 6, 0), (ACTIVITY_TYPE, 7, 0), (EQUIPMENT, 8, 0), (DAY_TYPE, 9, 0),
             (SLEEP_QUALITY, 10, 0), (DAY, 11, 0), (MONTH, 12, 0)]

    def __init__(self, root=None):
        self.__root = root
        self.diary_name_label = tk.StringVar()
        self._vars = {}
        for i in GraphGUI.MENUS:
            self._vars[i[0]] = tk.StringVar()
            self._vars[i[0]].set(i[0])

        self.__menu_buttons = {}
        self.__set_up_gui()

    def set_controller(self, gui_controller):
        self.__controller = gui_controller

    def set_option_menu_items(self, button_name, items):
        menu = self.__menu_buttons[button_name]["menu"]
        menu.delete(0, "end")
        for i in items:
            menu.add_command(label=i, command=lambda value=i: self._vars[button_name].set(value))
        self._vars[button_name].set(items[0])

    def selected_vars(self):
        d = {}
        for k,v in self._vars.items():
            if v.get() != ALL:
                d[k] = v.get()
        return d

    def _series_name(self):
        return ':'.join(v for v in self.selected_vars().values())

    def _open_diary(self):
        file_name = filedialog.askopenfilename(initialdir='/~', title='Select file', filetypes=[('JSON', '*.json'),
                                                                                                ('SQLITE', '*.db')])
        self.__controller.set_training_diary_data_frame(file_name)

    def _add_graph(self):
        selection = self.tree.selection()
        names = []
        for s in selection:
            print(self.tree.item(s)['values'][1])
            names.append(self.tree.item(s)['values'][1])
        self.__controller.get_df_for_series(names).plot()
        plt.show()

    def _add_bar(self):
        selection = self.tree.selection()
        values = self.__controller.get_series(self.tree.item(selection[0])['values'][1])
        values.plot(kind='bar')
        plt.show()

    def _heat_map(self):
        selection = self.tree.selection()
        if len(selection) < 2:
            return
        x = self.__controller.get_series(self.tree.item(selection[0])['values'][1])
        y = self.__controller.get_series(self.tree.item(selection[1])['values'][1])

        plt.hexbin(x, y, gridsize=20, cmap=cm.hot, bins=None)
        plt.axis([x.min(), x.max(), y.min(), y.max()])
        plt.grid(True, linestyle='-', alpha=0.5)

        cb = plt.colorbar()
        cb.set_label('observations')
        plt.show()

    def _scatter(self):
        selection = self.tree.selection()
        if len(selection) < 2:
            return
        x = self.__controller.get_series(self.tree.item(selection[0])['values'][1]).values
        y = self.__controller.get_series(self.tree.item(selection[1])['values'][1]).values

        d = self.__controller.get_scatter_data(self.tree.item(selection[0])['values'][1],
                                               self.tree.item(selection[1])['values'][1])

        x = d['x']
        y = d['y']

        c, p1 = polyfit(x, y, 1)

        # start with a rectangular Figure
        fig = plt.figure()
        gs = gridspec.GridSpec(3, 3)

        axMain = fig.add_subplot(gs[1:, :2])
        ax1 = fig.add_subplot(gs[0, :2], sharex=axMain)
        ax2 = fig.add_subplot(gs[1:, 2], sharey=axMain)

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)

        # the scatter plot:
        axMain.scatter(x, y)
        # add best fit
        axMain.plot(x, c + p1 * x, color='red', dashes=[3,3])

        min_x = np.nanmin(x)
        max_x = np.nanmax(x)
        x_width = (max_x - min_x) / 20
        min_y = np.nanmin(y)
        max_y = np.nanmax(y)
        y_width = (max_y - min_y) / 20
        xbins = np.arange(min_x, max_x + x_width, x_width)
        ybins = np.arange(min_y, max_y + y_width, y_width)

        ax1.hist(x, bins=xbins)
        ax2.hist(y, bins=ybins, orientation='horizontal')
        plt.subplots_adjust(wspace=0, hspace=0)

        plt.show()

    def _add_series(self):
        # selection = self.tree.focus()
        vars = self.selected_vars()
        count = self.__controller.create_series(self._series_name(), **vars)
        self.tree.insert('','end', text='Series', values=(count,self._series_name()))

    def __set_up_gui(self):

        self.td_label = tk.Label(self.__root, textvariable=self.diary_name_label)
        self.td_label.grid(row=0, column=1, columnspan=5, sticky='nsew')
        load_file_button = tk.Button(self.__root, text='Open Training Diary', command=self._open_diary)
        load_file_button.grid(row=0, column=0, sticky='nsew')

        series_label = tk.Label(self.__root, text='Series:')
        series_label.grid(row=1, column=0, sticky='nsew')
        series_add_button = tk.Button(self.__root, text='Add', command=self._add_series)
        series_add_button.grid(row=1, column=1, sticky='nsew')
        add_graph_button = tk.Button(self.__root, text='Scatter', command=self._scatter)
        add_graph_button.grid(row=1, column=2, sticky='nsew')
        add_graph_button = tk.Button(self.__root, text='Heat Map', command=self._heat_map)
        add_graph_button.grid(row=1, column=3, sticky='nsew')
        add_graph_button = tk.Button(self.__root, text='Bar Graph', command=self._add_bar)
        add_graph_button.grid(row=1, column=4, sticky='nsew')
        add_graph_button = tk.Button(self.__root, text='Line Graph', command=self._add_graph)
        add_graph_button.grid(row=1, column=5, sticky='nsew')

        for i in GraphGUI.MENUS:
            self.__menu_buttons[i[0]]  = tk.OptionMenu(self.__root, self._vars[i[0]], ())
            tk.Label(self.__root, text=i[0]).grid(row=i[1], column=i[2])
            self.__menu_buttons[i[0]].grid(row=i[1], column=(i[2]+1), sticky='nsew')

        tree_frame = tk.Frame(self.__root, width=50, height=200)
        tree_frame.grid(row=2, column=2, rowspan=11, columnspan=4, sticky='nsew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # self.tree = ttk.Treeview(tree_frame, columns=[i[0] for i in GraphGUI.MENUS])
        self.tree = ttk.Treeview(tree_frame, columns=['Count', 'Description'])
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky=tk.NS)

        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        self.tree.configure(xscrollcommand=hsb.set,
                            yscrollcommand=vsb.set)

        self.tree.heading('#0', text='Name')
        self.tree.heading('Count', text='Count')
        self.tree.heading('Description', text='Description')

        self.tree.column('#0', width=75, stretch=False)
        self.tree.column('Count', width=50, stretch=False)
        self.tree.column('Description', width=500, stretch=True)
