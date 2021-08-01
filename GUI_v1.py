import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import style
style.use('seaborn-darkgrid')

global canvas
global fig
fig = Figure()
canvas = FigureCanvasQTAgg(fig)

global data
data = [dict() for _ in range(8)]

global age_index, height_index, weight_index, state_index, city_index, name_index, surname_index, gender_index

age_index		= 0
height_index	= 1
weight_index	= 2
state_index		= 3
city_index		= 4
name_index		= 5
surname_index	= 6
gender_index	= 7

class PageWindow(qtw.QMainWindow):
	gotoSignal = qtc.pyqtSignal(str)

	def trigger_gotoSignal(self, name):
		self.gotoSignal.emit(name)

class SetupPageWindow(PageWindow):
	def __init__(self, parent):
		super().__init__()

		self.parent = parent
		self.load_file_button = qtw.QPushButton('Load Data File', clicked=self.get_data_file_name)
		self.load_file_button.setProperty("setup", "true")

		self.plot_radio = qtw.QButtonGroup()
		self.pie_plot_radio = qtw.QRadioButton("Pie charts", clicked=lambda: self.set_plot_type("pie"))
		self.plot_radio.addButton(self.pie_plot_radio)
		self.hist_plot_radio = qtw.QRadioButton("Histograms", clicked=lambda: self.set_plot_type("hist"))
		self.plot_radio.addButton(self.hist_plot_radio)
		self.line_plot_radio = qtw.QRadioButton("Line Graphs", clicked=lambda: self.set_plot_type("line"))
		self.plot_radio.addButton(self.line_plot_radio)

		self.goto_plotpage_button = qtw.QPushButton('Start Ploting >', clicked=self.goto_plotpage, objectName="navButton")
		self.goto_plotpage_button.setProperty("nav", "true")
		self.goto_plotpage_button.setProperty("setup", True)

		self.main_widget = qtw.QWidget()
		self.main_widget.setLayout(qtw.QVBoxLayout())

		self.main_widget.layout().setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
		self.main_widget.layout().addWidget(self.load_file_button)
		self.main_widget.layout().addWidget(self.pie_plot_radio)
		self.main_widget.layout().addWidget(self.hist_plot_radio)
		self.main_widget.layout().addWidget(self.line_plot_radio)
		self.main_widget.layout().addWidget(self.goto_plotpage_button)

		self.setCentralWidget(self.main_widget)

	def get_data_file_name(self):
		self.data_file_name, _ = qtw.QFileDialog.getOpenFileName(self, "open citizen text data file", "citizens.txt", "Text files (*.txt)")

		if self.data_file_name != "":
			self.process_data_file()

	def process_data_file(self):
		self.parent.data_file_name = self.data_file_name
		input_file = open(self.data_file_name, 'r')

		persons = []
		for line in input_file:
			try:
				persons.append(Person(*(line[:-1].split(', '))))
			except:
				qtw.QMessageBox.critical(self.parent, "error", f"loaded file '{self.parent.data_file_name}' is not according to format")
				return

		input_file.close()

		for i in persons:
			p = [i]
			data[age_index][i.age]			= data[age_index].get(i.age, [])		 + p
			data[height_index][i.height]	= data[height_index].get(i.height, [])	 + p
			data[weight_index][i.weight]	= data[weight_index].get(i.weight, [])	 + p
			data[state_index][i.state]		= data[state_index].get(i.state, [])	 + p
			data[city_index][i.city]		= data[city_index].get(i.city, [])		 + p
			data[name_index][i.name]		= data[name_index].get(i.name, [])		 + p
			data[surname_index][i.surname]	= data[surname_index].get(i.surname, []) + p
			data[gender_index][i.gender]	= data[gender_index].get(i.gender, [])	 + p
		del persons
		self.parent.refresh_statusbar()

	def set_plot_type(self, type):
		self.parent.plot_type = type
		self.parent.refresh_statusbar()

	def goto_plotpage(self):
		flag = False

		if self.pie_plot_radio.isChecked() or self.hist_plot_radio.isChecked() or self.line_plot_radio.isChecked():
			if self.parent.data_file_name != "Not selected yet":
				flag = True

		if flag:
			self.trigger_gotoSignal('plot')
		else:
			qtw.QMessageBox.information(self.parent, "access not allowed", "please load data file or select plot type")

	def refresh(self):
		self

class PlotPageWindow(PageWindow):
	def __init__(self, parent):
		super().__init__()

		self.parent = parent
		self.dock = qtw.QDockWidget("plot controls")

		self.sub_dock = qtw.QWidget()
		self.sub_dock.setLayout(qtw.QGridLayout())

		self.goto_setuppage_button = qtw.QPushButton('< Setup Page', clicked=self.goto_setuppage)
		self.goto_setuppage_button.setProperty("nav", "true")
		self.plot_button = qtw.QPushButton('plot', clicked=lambda: self.generate_plot(self.parent.plot_type))

		self.key_checkboxes = qtw.QWidget()
		self.key_checkboxes.setLayout(qtw.QGridLayout())
		self.key_checkboxes.layout().setAlignment(qtc.Qt.AlignmentFlag.AlignTop)

		self.key_checkboxes.layout().addWidget(qtw.QCheckBox('All', clicked=self.key_selected))
		for i in range(1,6):
			for j in range(2):
				checkbox = qtw.QCheckBox('cum')
				checkbox.toggled.connect(self.key_selected)
				self.key_checkboxes.layout().addWidget(checkbox, i, j)

		self.pie_group_index_input = qtw.QComboBox()
		items = ['states', 'city', 'age', 'gender', 'name', 'surname', 'height', 'weight']
		self.pie_group_index_input.addItems(items)
		self.pie_group_index_input.currentTextChanged.connect(self.set_group_index)

		self.hist_group_index_input = qtw.QComboBox()
		self.hist_group_index_input.addItems(items)
		self.hist_group_index_input.currentTextChanged.connect(self.set_group_index)

		self.pie_plot_filter_input = qtw.QComboBox()
		items = ['age', 'bmi', 'gender', 'height', 'weight']
		self.pie_plot_filter_input.addItems(items)
		self.pie_plot_filter_input.currentTextChanged.connect(self.set_plot_filter)

		self.line_plot_filter_input = qtw.QComboBox()
		items += ['states', 'city', 'name', 'surname']
		self.line_plot_filter_input.addItems(items)
		self.line_plot_filter_input.currentTextChanged.connect(lambda s: self.set_plot_filter(s, checkbox=True))

		self.pie_group_keys_input = qtw.QLineEdit()
		self.hist_group_keys_input = qtw.QLineEdit()
		self.line_group_keys_input = qtw.QLineEdit()

		self.pie_control_frame = qtw.QFrame()
		self.hist_control_frame = qtw.QFrame()
		self.line_control_frame = qtw.QFrame()
		self.pie_control_frame.setLayout(qtw.QGridLayout())
		self.hist_control_frame.setLayout(qtw.QGridLayout())
		self.line_control_frame.setLayout(qtw.QGridLayout())

		self.pie_input_label_gi = qtw.QLabel('Categorize Subpolts by Persons Atribute:')
		self.pie_input_label_pf = qtw.QLabel('Calculate % in individual pie plot by Persons Atribute:')
		self.pie_input_label_gk = qtw.QLabel('which catogory subplots to include:')
		self.pie_control_frame.layout().addWidget(self.pie_input_label_gi, 0, 0)
		self.pie_control_frame.layout().addWidget(self.pie_group_index_input, 1, 0)
		self.pie_control_frame.layout().addWidget(self.pie_input_label_pf, 2, 0)
		self.pie_control_frame.layout().addWidget(self.pie_plot_filter_input, 3, 0)
		self.pie_control_frame.layout().addWidget(self.pie_input_label_gk, 4, 0)
		self.pie_control_frame.layout().addWidget(self.pie_group_keys_input, 5, 0)

		self.hist_input_label_gi = qtw.QLabel('Histogram bins from Persons Atribute:')
		self.hist_input_label_gk = qtw.QLabel('which bins to include:')
		self.hist_control_frame.layout().addWidget(self.hist_input_label_gi, 0, 0)
		self.hist_control_frame.layout().addWidget(self.hist_group_index_input, 1, 0)
		self.hist_control_frame.layout().addWidget(self.hist_input_label_gk, 2, 0)
		self.hist_control_frame.layout().addWidget(self.hist_group_keys_input, 3, 0)

		self.line_input_label_pf = qtw.QLabel('Persons Atribute to check:')
		self.line_input_label_gk = qtw.QLabel('include if atribute is in:')
		self.line_control_frame.layout().addWidget(self.line_input_label_pf, 0, 0)
		self.line_control_frame.layout().addWidget(self.line_plot_filter_input, 1, 0)
		self.line_control_frame.layout().addWidget(self.line_input_label_gk, 2, 0)
		self.line_control_frame.layout().addWidget(self.line_group_keys_input, 3, 0)
		

		self.sub_dock.layout().setAlignment(qtc.Qt.AlignmentFlag.AlignTop)
		self.sub_dock.layout().addWidget(self.goto_setuppage_button, 1, 1)
		self.sub_dock.layout().addWidget(self.pie_control_frame, 2, 1)
		self.sub_dock.layout().addWidget(self.hist_control_frame, 3, 1)
		self.sub_dock.layout().addWidget(self.line_control_frame, 4, 1)
		self.sub_dock.layout().addWidget(self.key_checkboxes, 5, 1)
		self.sub_dock.layout().addWidget(self.plot_button, 6, 1)

		self.dock.setFeatures(qtw.QDockWidget.DockWidgetFeature.DockWidgetFloatable | qtw.QDockWidget.DockWidgetFeature.DockWidgetMovable)
		self.dock.setWidget(self.sub_dock)
		self.addDockWidget(qtc.Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

		self.setCentralWidget(canvas)

	def goto_setuppage(self):
		self.trigger_gotoSignal('setup')

	def refresh(self):
		if self.parent.plot_type == 'pie':
			self.set_group_index(self.pie_group_index_input.currentText())
			self.set_plot_filter(self.pie_plot_filter_input.currentText())
			
			pie_plot(state_index, lambda s: s in ['Gujarat', 'Maharashtra', 'Delhi', 'Uttar Pradesh', 'Rajasthan', 'Karnataka'], gender_p_filter, 3, 2)
			
		elif self.parent.plot_type == 'hist':
			self.set_group_index(self.hist_group_index_input.currentText())
			
			histogram_plot(city_index, lambda s: s in ['Ahmedabad', 'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Vadodara'])

		elif self.parent.plot_type == 'line':
			self.set_plot_filter(self.line_plot_filter_input.currentText())

			line_plot(gender_p_filter, [0])

		self.display_controls(self.parent.plot_type)

	def display_controls(self, plot_type):
		self.pie_control_frame.hide()
		self.hist_control_frame.hide()
		self.line_control_frame.hide()

		if plot_type == 'pie':
			self.pie_control_frame.show()
			self.display_checkboxes(self.pie_group_index_input.currentText())
		elif plot_type == 'hist':
			self.hist_control_frame.show()
			self.display_checkboxes(self.hist_group_index_input.currentText())
		elif plot_type == 'line':
			self.line_control_frame.show()

	def display_checkboxes(self, key):
		self.pie_group_keys_input.setText('')
		self.hist_group_keys_input.setText('')
		self.line_group_keys_input.setText('')
	
		flag = True
		if key.lower() in ['age', 'bmi', 'gender', 'height', 'weight']:
			if self.parent.plot_type != 'line' and key.lower() != 'gender':
				flag = False
			else:
				if self.parent.plot_type == 'pie':
					temp = self.pie_plot_filter_input.currentText()
				elif self.parent.plot_type == 'line':
					temp = self.line_plot_filter_input.currentText()
				else:
					temp = 'age'

				self.set_plot_filter(key)
				options = pf(labels=True)
				self.set_plot_filter(temp)

		elif key.lower() in ['states', 'city', 'name', 'surname']:
			options = data[gi].keys()

		j = 1
		total = self.key_checkboxes.layout().count()

		if flag:	
			self.key_checkboxes.layout().itemAt(0).widget().setChecked(False)
			for string in options:
				if j == total:
					return
				if string == '':
					break
				self.key_checkboxes.layout().itemAt(j).widget().setText(string)
				self.key_checkboxes.layout().itemAt(j).widget().setChecked(False)
				j+=1

		while j != total:
			self.key_checkboxes.layout().itemAt(j).widget().setText('----')
			self.key_checkboxes.layout().itemAt(j).widget().setChecked(False)
			j+=1

	def key_selected(self):
		checkbox = self.sender()
		
		if self.parent.plot_type == 'pie':
			line_edit = self.pie_group_keys_input
		elif self.parent.plot_type == 'hist':
			line_edit = self.hist_group_keys_input
		elif self.parent.plot_type == 'line':
			line_edit = self.line_group_keys_input

		current_text = line_edit.text().lower()
		keys = current_text.split(',')
		
		box_text = checkbox.text()

		if box_text == 'All':
			if checkbox.isChecked():
				keys = ['all'] + keys
			else:
				keys = keys[1:]
		else:
			if box_text.lower() not in keys and checkbox.isChecked():
				keys.append(box_text)
			elif box_text.lower() in keys and not checkbox.isChecked():
				index = 0
				for i, text in enumerate(keys):
					if text == box_text.lower():
						index = i
						break
				keys = keys[:index] + keys[index+1:]

		current_text = ','.join(keys)
		line_edit.setText(current_text)

	def set_group_index(self, key):
		global gi
		if key == 'states':
			gi = state_index
		elif key == 'city':
			gi = city_index
		elif key == 'age':
			gi = age_index
		elif key == 'gender':
			gi = gender_index
		elif key == 'name':
			gi = name_index
		elif key == 'surname':
			gi = surname_index
		elif key == 'height':
			gi = height_index
		elif key == 'weight':
			gi = weight_index

		self.display_checkboxes(key)

	def set_plot_filter(self, key, checkbox=False):
		self
		global pf
		if key == 'age':
			pf = age_p_filter
		elif key == 'bmi':
			pf = bmi_p_filter
		elif key == 'gender':
			pf = gender_p_filter
		elif key == 'height':
			pf = height_p_filter
		elif key == 'weight':
			pf = weight_p_filter
		else:
			pf = 'lambda_filter'

		if checkbox:
			self.display_checkboxes(key)

	def generate_plot(self, plot_type):
		global gi, gf, pf
		if plot_type == 'pie':
			p_x = 5
			p_y = 4

			values = self.pie_group_keys_input.text().lower().split(',')
			if values[0] == 'all':
				gf = lambda _: True
			else:
				gf = lambda s: str(s).lower() in values

				l = len(values)
				if l==1:
					p_x = 1
					p_y = 1
				else:
					max_lim = int(l**0.5+1)
					for i in range(max_lim, 1, -1):
						if l % i == 0:
							p_x = i
							p_y = int(l / i)
							break
					
			pie_plot(gi, gf, pf, p_x, p_y)
			
		elif plot_type == 'hist':

			values = self.hist_group_keys_input.text().lower().split(',')
			if values[0] == 'all':
				gf = lambda _: True
			else:
				gf = lambda s: str(s).lower() in values

			histogram_plot(gi, gf)

		elif plot_type == 'line':

			values = self.line_group_keys_input.text().lower().split(',')
			
			if values[0] == 'all':
				pf = lambda _: 0
				pf_s = [0]
			elif pf == 'lambda_filter':
				pf = lambda p: p.state in values or p.city in values or p.name in values or p.surname in values
				pf_s = [True]
			else:
				selected_ints = []
				labels = pf(labels=True)
				for i, label in enumerate(labels):
					if label in values:
						selected_ints.append(i)
				
				pf_s = selected_ints

			line_plot(pf, pf_s)

class Window(qtw.QMainWindow):
	def __init__(self):
		super().__init__()

		self.stacked_widget = qtw.QStackedWidget()
		self.setCentralWidget(self.stacked_widget)

		self.stacked_pages = {}

		self.data_file_name = "Not selected yet"
		self.plot_type = "Not selected yet"

		setup_page = SetupPageWindow(self)

		self.status_bar = self.statusBar()
		self.change_top_page("setup")

		plot_page = PlotPageWindow(self)

		self.add_page(setup_page, "setup")
		self.add_page(plot_page, "plot")

		self.setWindowTitle("Citizen Data Visualization App")
		self.setStyle(qtw.QStyleFactory.create("Fusion"))
		self.setGeometry(50, 50, 1000, 500)

		self.show()

	def add_page(self, widget, name):
		self.stacked_pages[name] = widget
		self.stacked_widget.addWidget(widget)

		if isinstance(widget, PageWindow):
			widget.gotoSignal.connect(self.change_top_page)

	def change_top_page(self, name):
		self.refresh_statusbar()
		if name in self.stacked_pages:
			new_top_page = self.stacked_pages[name]
			new_top_page.refresh()
			self.stacked_widget.setCurrentWidget(new_top_page)
	
	def refresh_statusbar(self):
		self.status_bar.showMessage("Data File: " + self.data_file_name + f"{'': <50}" + "Plot type: " + self.plot_type)


class Person:
	def __init__(self, p_id, name, surname, age, gender, state, city, weight, height):
		self.p_id = p_id
		self.name = name
		self.surname = surname
		self.age = int(age)
		self.gender = gender
		self.city = city
		self.state = state
		self.weight = int(weight)
		self.height = int(height)

	def __str__(self):
		return  (
					f"\n{'':-^62}"
					f"\n|{f' Name:  {self.name:<10} Sername: {self.surname:<10} p_id: {self.p_id}':60}|"
					f"\n|{f' age:   {self.age:<10} gender: {self.gender}':60}|"
					f"\n|{f' weight:{self.weight:<10} height: {self.height}':60}|"
					f"\n|{f' state: {self.state:<10} city: {self.city}':60}|"
					f"\n{'':-^62}"
				)

	def __repr__(self):
		return f'{self.p_id}, {self.name}, {self.surname}, {self.age}, {self.gender}, {self.state}, {self.city}, {self.weight}, {self.height}\n'

def pie_plot(group_index, group_filter, plot_filter, x, y):
	""" 
		a function to plot pie chart

		global data:list(dict) is used for the chart data
		plots one or more pie charts for every key in data[group_index], where each person in the list associated by a key
		is catogorized and calculated(in %) based on wieights(0 to 5) returned by plot_filter(Person)

		group_index: index of data:list()
		group_filter: a function to filter keys of data[group_index]
		plot_filter: a function to filter persons in data[group_index][key]

	"""
	global fig
	fig.clf()

	states_to_plot = filter(group_filter, data[group_index])

	for index, state in enumerate(states_to_plot):
		count = [0 for _ in range(5)]

		for person in data[group_index][state]:

			i = plot_filter(person)
			count[i] += 1
		
		total_person = sum(count)
		gender_percentages = [round(i/total_person, 2)*100 for i in count]

		try:
			axes = fig.add_subplot(x, y, index+1)
		except ValueError:
			break

		all_labels = plot_filter(labels=True)
		labels = [all_labels[i] if p!=0 else '' for i,p in enumerate(gender_percentages)]
		axes.pie(gender_percentages, labels=labels, autopct= lambda x: '' if x==0 else f'{x:.0f}%')
		axes.set_title(state)

	global canvas
	canvas.draw()

def histogram_plot(group_index, group_filter):
	global fig
	fig.clf()

	person_count_list = [len(data[group_index][person]) for person in filter(group_filter , data[group_index])]
	bar_ticks = [i for i in filter(group_filter, data[group_index])]

	axes = fig.add_subplot(111)
	axes.bar(bar_ticks, person_count_list, edgecolor='k')
	axes.set_ylabel('count')
	
	fig.autofmt_xdate(rotation=45)

	global canvas
	canvas.draw()

def line_plot(plot_filter, pf_select):
	global fig
	fig.clf()

	ages = []
	avg_h = []
	avg_w = []

	for age in data[age_index]:
		total_height = 0
		total_weight = 0
		n = 0
		ages.append(age)
		for person in data[age_index][age]:
			if plot_filter(person) in pf_select:
				total_height += person.height
				total_weight += person.weight
				n += 1

		if n == 0:
			ages.pop()
		else:
			avg_h.append(round(total_height/n, 2))
			avg_w.append(round(total_weight/n, 2))

	avg_h = [avg for _, avg in sorted(zip(ages, avg_h))]
	avg_w = [avg for _, avg in sorted(zip(ages, avg_w))]
	ages.sort()

	axes = fig.add_subplot(111)

	axes.plot(ages, avg_h, marker='.', markerfacecolor='k', label='average height')
	axes.plot(ages, avg_w, marker='.', markerfacecolor='k', label='average weight')
	
	axes.set_xlabel('average height/weight per age')
	axes.set_ylabel('weight(kg) | height (cm)')
	axes.legend()
	
	global canvas
	canvas.draw()

# A plot_filter function used for pie_plot(plot_filter)
def age_p_filter(person=None, labels=False):
	if labels:
		return ['toddler', 'teen', 'adult', '', '']

	if person.age < 13:
		return 0
	elif 13 <= person.age < 18:
		return 1
	else:
		return 2

# A plot_filter function used for pie_plot(plot_filter)
def gender_p_filter(person=None, labels=False):
	if labels:
		return ['male', 'female', '', '', '']

	if person.gender == 'male':
		return 0
	else:
		return 1

# A plot_filter function used for pie_plot(plot_filter)
def height_p_filter(person=None, labels=False):
	if labels:
		return ['<150', '150+', '170+', '', '']

	if person.height < 150:
		return 0
	elif 150 <= person.height <= 170:
		return 1
	else:
		return 2

# A plot_filter function used for pie_plot(plot_filter)
def weight_p_filter(person=None, labels=False):
	if labels:
		return ['<40', '40+', '60+', '', '']

	if person.weight < 40:
		return 0
	elif 40 <= person.weight <= 60:
		return 1
	else:
		return 2

# A plot_filter function used for pie_plot(plot_filter)
def bmi_p_filter(person=None, labels=False):
	if labels:
		return ['under w', 'normal', 'over w', 'obese', '']

	bmi = person.weight/(person.height/100)**2

	if bmi < 18.5:
		return 0
	elif 18.5 <= bmi < 25:
		return 1
	elif 25 <= bmi < 30:
		return 2
	else:
		return 3

stylesheet = '''
'''
if __name__ == '__main__':
	app = qtw.QApplication([])
	app.setStyleSheet(stylesheet)
	mw = Window()
	app.exec_()