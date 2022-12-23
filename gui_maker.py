from tkinter import *
from tkinter import ttk
import threading
from status_info import Status
from file_searcher import File_Searcher

class GUI:

	def gen_dir_frame(self, gui_app, file_searcher): # window to set directory
		frame1 = LabelFrame(gui_app, 
					text="Diretory Setter Window",
					padx=20, pady=80)

		frame1.grid(row=0, column=0)

		cur_dir_label = Label(frame1, text= "Current Working DIrectory:\n" + file_searcher.cur_dir)
		cur_dir_label.pack()

		empty_label = Label(frame1)
		empty_label.pack()

		def set_dir_action():
			dir_flag = file_searcher.set_directory()
			cur_dir_label.config(text=file_searcher.cur_dir)

			# make the search result empty as new dir
			if dir_flag:
				self.render_search_list([])
				self.search_status.reset_all()

		set_dir_button = Button(frame1, text="Set New Directory", command=set_dir_action)
		set_dir_button.pack()


	def gen_index_progress_bar(self, gui_app):
		global progress_bar, progress_text, index_frame

		index_frame = LabelFrame(gui_app, 
					text="Indexing Progress",
					padx=20, pady=150)

		index_frame.grid(row=1, column=0)

		progress_bar = ttk.Progressbar(index_frame, 
						orient='horizontal', mode='determinate', length=400)

		progress_bar.pack()

		progress_text = Label(index_frame, text="Indexing Progress: Currently Not Running")
		progress_text.pack()

		self.index_status = Status(index_frame, progress_bar, progress_text, "Indexing")


	def search_list_frame(self, gui_app):
		frame_file_list = LabelFrame(gui_app,
						text="Found Files",
						padx=20, pady=20)

		frame_file_list.grid(row=1, column=1)

		self.file_list_text = Text(frame_file_list, height=20, width=50, state=DISABLED)

		yscrollbar = Scrollbar(gui_app, orient='vertical', command=self.file_list_text.yview)
		yscrollbar.grid(row=1, column=2, sticky=NS)
		self.file_list_text['yscrollcommand'] = yscrollbar.set

		self.file_list_text.pack()


	def render_search_list(self, file_list):
		founded_files = '\n\n'.join(list(file_list))

		self.file_list_text.config(state=NORMAL)

		self.file_list_text.delete(1.0, "end-1c")
		self.file_list_text.insert("end-1c", founded_files)

		self.file_list_text.config(state=DISABLED)


	def gen_search_frame(self, gui_app, file_searcher): # window to search files

		frame2 = LabelFrame(gui_app,
						text="File Search Window",
						padx=20, pady=80)

		frame2.grid(row=0, column=1)

		search_instruction = Label(frame2, text="Enter your search text:")
		search_instruction.pack()

		search_box = Text(frame2, height=2, width=50)
		search_box.pack()

		def search_action(cur_status, last_tid):
			search_key = search_box.get("1.0",'end-1c')

			search_result = file_searcher.search_file(search_key, cur_status, last_tid)
			if type(search_result) == list:
				self.render_search_list(search_result)

		tid = 0
		def thread_search():
			nonlocal tid
			tid += 1

			# make the search result empty
			self.render_search_list([])

			cur_search_status = self.search_status.copy()
			cur_search_status.set_tid(lambda:tid)
			
			# utilize threading for searchng
			proc = threading.Thread(target=search_action, args=(cur_search_status, lambda:tid,), name=str(tid))
			proc.daemon = True
			proc.start()

		search_file_button = Button(frame2, text="Search File", command=thread_search)

		search_progress_bar = ttk.Progressbar(frame2, 
						orient='horizontal', mode='determinate', length=400)

		search_progress_text = Label(frame2, text="Searching Progress: Currently Not Running")

		self.search_status = Status(frame2, search_progress_bar, search_progress_text, "Searching")

		search_file_button.pack()
		search_progress_bar.pack()
		search_progress_text.pack()

	def init_gui(self):
		self.gui_app = Tk()
		self.gui_app.title("Search Your File")
		# self.gui_app.geometry("500x500")

		self.gen_index_progress_bar(self.gui_app)

		file_searcher = File_Searcher(self.index_status)
		self.gen_dir_frame(self.gui_app, file_searcher)
		self.search_list_frame(self.gui_app)
		self.gen_search_frame(self.gui_app, file_searcher)

		self.gui_app.mainloop()
