from multiprocessing import Process
from queue import Queue
from crawler import Crawler
from pybloom import BloomFilter
import time, os


class ProgrammeeProcess(Process):
	def __init__(self, user):
		super().__init__()
		self.crawler = Crawler()
		self.bf = BloomFilter(capacity=1000000, error_rate=0.001)
		self.queue = Queue()
		self.queue.put(user)

	def run(self):
		while not self.queue.empty():
			self.user = self.queue.get()
			girl = self.crawler.get_girl(self.user)
			if girl != None and self.queue.qsize() <= 100:
				fos = self.crawler.get_all_followees(girl.user)
				if fos != None:
					for each in fos:
						if not each in self.bf:
							print(girl.user + ' ' + each)
							print(self.queue.qsize())
							self.bf.add(each)
							self.queue.put(each)

queue = Queue()
processes = []

directory = 'programmee'
users = os.listdir(directory)
for each in users:
	print(each)
	queue.put(each)

while not queue.empty():
	user = queue.get()
	processes.append(ProgrammeeProcess(user))

for each in processes:
	each.start()
for each in processes:
	each.join()
