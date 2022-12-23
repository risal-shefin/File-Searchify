from tkinter import *
from tkinter import filedialog
import os, threading
import pickle
import math
from suffix_array import SuffixArray

class File_Searcher:
	cur_dir = os.getcwd()  # current working directory
	index_db = dict()
	index_db_name = "index_db.bin"  # the filename of the indexing db
	index_status = None # Status Object

	def get_file_dir(self, filename): # append filename to the current working directory
		return self.cur_dir + '/' + filename


	def init_index_db(self): # initialize the indexing db from the storage
		self.index_db.clear()
		if os.path.exists(self.get_file_dir(self.index_db_name)) != True:
			return
		
		db_file = open(self.get_file_dir(self.index_db_name), "rb")
		self.index_db = pickle.load(db_file)

	def is_expired(self): # check if current dir modified time > db creation time
		if os.path.exists(self.get_file_dir(self.index_db_name)) != True:
			return True

		db_time = os.path.getmtime(self.get_file_dir(self.index_db_name))
		dir_time = os.path.getmtime(self.cur_dir)
		
		if dir_time > db_time:
			return True

		return False


	def build_index_db_if_expired(self): # only build new indexing if the existing becomes expired

		if self.is_expired() == False:
			self.index_status.full_complete()
			return

		# clear old indexing db
		self.index_db.clear()
		self.index_status.reset_iter()
		cur_dir = self.cur_dir

		db_file = open(cur_dir + '/' + self.index_db_name, "wb") # create db file
		db_file.close()

		files = os.listdir(cur_dir)
		files = [item for item in files if os.path.isfile(self.get_file_dir(item))] # only files are allowed

		filename_string = "\0".join(files) + "\0"
		filename_string_length = len(filename_string)

		# calculate a rough upper bound estimation
		# rough_indexing_iter = 6 * filename_string_length * math.ceil(math.log(filename_string_length, 2)) + 5*filename_string_length
		rough_indexing_iter = math.ceil(math.log(filename_string_length, 2)) + 1
		self.index_status.set_iter(rough_indexing_iter)
		self.index_status.upd_iter()

		# build suffix array
		suffixArray = SuffixArray()
		suffixArray.initArray(filename_string)
		suffixArray.buildSA(self.index_status)

		# build new indexing db
		self.index_db[filename_string] = suffixArray.SA

		db_file = open(cur_dir + '/' + self.index_db_name, "wb") # open db file
		pickle.dump(self.index_db, db_file) # save the db on storage
		db_file.close()

		self.index_status.full_complete() # indexing 100% done
		

	def set_directory(self): # set the specified directory
		new_dir = filedialog.askdirectory(title="Select a directory")
		if not new_dir:
			return False

		self.cur_dir = new_dir
		self.init_index_db()
		threading.Thread(target=self.build_index_db_if_expired, daemon=True).start() # if the existing is expired
		return True

	def search_file(self, search_key, cur_status, last_tid):
		cur_status.reset_iter()

		self.build_index_db_if_expired() # if db is expired. search after the db

		def isBad():
			return str(last_tid()) != threading.current_thread().name

		if isBad(): # New search request has appeared
			return "TERMINATED"

		if len(search_key) == 0:
			cur_status.full_complete()
			if isBad():
				return "TERMINATED"
			return []

		index_info = list(self.index_db.items())[0]
		filename_string = index_info[0]
		suffix_array = index_info[1]

		sa_length = text_length = len(filename_string)
		key_length = len(search_key)

		marked_idx = set()	# to ensure that a file is not taken multiple times

		# progress bar calc
		search_upd_block = max(1, sa_length//20)
		rough_search_iter = math.ceil(math.log(sa_length)) + sa_length//search_upd_block + 1
		cur_status.set_iter(rough_search_iter)
		cur_status.upd_iter()

		if isBad():
			return "TERMINATED"

		def lexi_comp(start_idx):
			for i in range(key_length):
				if isBad():
					return "TERMINATED"

				ch1 = search_key[i]; ch2 = "\0"

				cur_idx = start_idx+i
				if cur_idx in marked_idx:
					return 2 # index marked already
				if cur_idx < text_length:
					ch2 = filename_string[cur_idx]

				if ch1 > ch2:
					return 1  # search key greater
				elif ch1 < ch2:
					return -1  # search key smaller

			return 0 # equal


		def find_first():
			lo = 0; hi = sa_length - 1
			result_index = -1

			while lo <= hi:
				mid = (lo+hi) // 2
				comp_val = lexi_comp(suffix_array[mid])
				if isBad():
					return "TERMINATED"

				if comp_val < 0:
					hi = mid - 1
				elif comp_val > 0:
					lo = mid + 1
				else:
					result_index = mid
					hi = mid - 1

				cur_status.upd_iter()

			return result_index

		first_match_index = find_first()
		
		if isBad():
			return "TERMINATED"

		files_list = list()

		if first_match_index == -1:
			cur_status.full_complete()
			if isBad():
				return "TERMINATED"
			return files_list

		cnt = 0
		for i in range(first_match_index, sa_length):
			comp_val = lexi_comp(suffix_array[i])
			if isBad():
				return "TERMINATED"

			if comp_val == 2:
				continue
			elif comp_val != 0:
				break

			l = r = suffix_array[i]

			while filename_string[r] != "\0":
				if isBad():
					return "TERMINATED"
				marked_idx.add(r)
				r += 1

			while l>=0 and filename_string[l] != "\0":
				if isBad():
					return "TERMINATED"
				marked_idx.add(l)
				l -= 1

			files_list.append(filename_string[l+1:r])

			cnt += 1
			if cnt%search_upd_block == 0:	# update after search_upd_block iterations
				cur_status.upd_iter()


		cur_status.full_complete()

		if isBad():
			return "TERMINATED"

		return files_list

	def __init__(self, index_status): # Intialize when the object of this is created
		self.index_status = index_status
		self.init_index_db()
		threading.Thread(target=self.build_index_db_if_expired, daemon=True).start() # utilize threading for heavy task
