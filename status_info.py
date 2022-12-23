import threading

class Status:
	bar = None; text = None; parent_frame = None
	tot_iter = 1; done_iter = 0
	type_msg = str()
	last_tid = None

	def isBadThread(self):
		return self.last_tid != None and str(self.last_tid()) != threading.current_thread().name

	def set_tid(self, tid):
		self.last_tid = tid

	def show_status(self):
		percentage = min(100, self.done_iter/self.tot_iter * 100)

		msg =  self.type_msg + " Progress: %0.2f" %(percentage) + "%"
		if(self.done_iter >= self.tot_iter):
			msg += " Completed!"

		if self.isBadThread(): # Later requests have already arrived
			return

		self.bar['value'] = percentage
		self.text.config(text=msg)
		self.parent_frame.update()

	def reset_all(self):
		self.done_iter = 0
		self.tot_iter = 1

		if self.isBadThread(): # Later requests have already arrived
			return
			
		self.bar['value'] = 0
		self.text.config(text= self.type_msg + " Progress: Currently Not Running")
		self.parent_frame.update()

	def upd_iter(self):
		self.done_iter += 1
		self.show_status()

	def set_iter(self, cnt):
		self.done_iter = 0
		self.tot_iter = cnt
		self.show_status()

	def reset_iter(self):
		self.set_iter(1)

	def full_complete(self):
		self.done_iter = self.tot_iter
		self.show_status()

	def __init__(self, frame, bar, text, type):
		self.parent_frame = frame
		self.bar = bar
		self.text = text
		self.type_msg = type

		self.done_iter = 0
		self.tot_iter = 1
		self.last_tid = None

	def copy(self):
		return Status(self.parent_frame, self.bar, self.text, self.type_msg)
