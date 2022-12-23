import sys

class SuffixArray:
	n = 0; t = 0; size = 0
	s = str()
	SA = list(); RA = list()
	tempSA = list(); tempRA = list()
	c = list()

	def initArray(self, _s):
		self.s = _s
		self.n = len(self.s)
		self.size = self.n

		self.SA = [0]*self.size; self.RA = [0]*2*self.size
		self.tempSA = [0]*self.size; self.tempRA = [0]*self.size
		self.c = [0]*max(sys.maxunicode+1, self.size)


	def countingSort(self, k):
		maxi = max(sys.maxunicode+1, self.n)
		for i in range(maxi):
			self.c[i] = 0

		for i in range(self.n):
			if i+k < self.n:
				self.c[ self.RA[i+k] ] += 1
			else:
				self.c[0] += 1

		sum = 0
		for i in range(maxi):
			t = self.c[i]
			self.c[i] = sum
			sum += t

		for i in range(0, self.n):
			if self.SA[i]+k < self.n:
				self.tempSA[self.c[self.RA[self.SA[i] + k] ] ] = self.SA[i]

				self.c[self.RA[self.SA[i] + k] ] += 1
			else:
				self.tempSA[self.c[0]] = self.SA[i]
				self.c[0] += 1

		for i in range(self.n):
			self.SA[i] = self.tempSA[i]


	def buildSA(self, index_status):
		for i in range(self.n):
			self.RA[i] = ord(self.s[i])
		
		for i in range(self.n):
			self.SA[i] = i

		k = 1
		while(k < self.n):
			self.countingSort(k)
			self.countingSort(0)

			self.tempRA[self.SA[0]] = r = 0

			for i in range(1, self.n):
				if(self.RA[self.SA[i]] == self.RA[self.SA[i - 1]] and self.RA[self.SA[i] + k] == self.RA[self.SA[i - 1] + k]):
					self.tempRA[self.SA[i]] = r
				else:
					r += 1
					self.tempRA[self.SA[i]] = r
				

			for i in range(0, self.n):
				self.RA[i] = self.tempRA[i]

			if(self.RA[self.SA[self.n-1]] == self.n -1):
				break

			k <<= 1

			index_status.upd_iter()
