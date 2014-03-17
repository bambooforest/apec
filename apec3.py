# APEC: A tool for automatic phonological analysis of field data
# Steven Moran & Shauna Eggers
# Proceedings of the 2006 E-MELD Workshop, Tools and Standards: the state of the art
# June 20-22, East Lansing, MI
# http://emeld.org/workshop/2006/proceedings.html

# last updated for QuantHistLing 2011-2013

import sys
import re
import operator # python-sort-a-dictionary-by-value

from optparse import OptionParser

default_features = 'english.fea'
multiphone_file = 'default.phn'

class Main(object):
	"""
	Main class; starts application
	"""
	# get input from user
	def getFile(self):
		self.infile = ''
		# TODO get file name from command line
		

	def readFlags(self):
		# TODO add usage stuff
		self.parser = OptionParser()
		self.parser.add_option("-d", dest="data_file", metavar="data_file", action="store", type="string", default="", help="File containing data for analysis.")
		self.parser.add_option("-t", dest="thong_file", metavar="thong_file", action="store", type="string", default="", help="File containing diphthongs or tripthongs data for analysis.")
		self.parser.add_option("-f", dest="feature_file", metavar="feature_file", action="store", type="string", default="english.fea", help="File containing features for phones.")
		self.parser.add_option("-p", dest="phone_file", metavar="phone_file", action="store", type="string", default="default.phn", help="File containing multicharacter phones.")
		self.parser.add_option("-e", dest="environs", action="store_true", help="Display as list of environments instead of phones.")
		self.parser.add_option("-v", dest="verbose", action="store_true", help="Print output as feature bundles.")
		self.parser.add_option("-w", dest="words", action="store_true", help="Print examples instead of counts for each environment.")
		self.parser.add_option("-l", dest="list", action="store_true", help="Print output as verticle list.")
		self.parser.add_option("-c", dest="distributions", action="store_true", help="Group output by complementary and contrastive distributions.")
		self.parser.add_option("-m", dest="min_pairs", action="store_true", help="Find minimal pairs.")		
		self.parser.add_option("-I", dest="interactive", action="store_true", help="Invoke interactive data analysis mode.")
		self.parser.add_option("-s", dest="syllable", action="store_true", help="Find syllable structure in data.")
		self.parser.add_option("-D", dest="distributions", action="store_true", help="Find contrastive and complementary distributions.")
		self.parser.add_option("--export-tabs", dest="export_tabs", action="store_true", help="Export results in tab delimited format.")
		self.parser.add_option("--export-commas", dest="export_commas", action="store_true", help="Export results as comma-separated values (CSV).")
#		self.parser.add_option("-h", dest="help", help="Help yo self.")
		(self.options, args) = self.parser.parse_args()

	def getUniqueSegments(self):
		input = Input()
		data = input.getUniqueSegments(self.options.data_file)

	def identifyThongs(self):
		input = Input()
		data = input.identifyThongs(self.options.data_file, self.options.thong_file)
		

	# call methods
	def findPhones(self):
		input = Input()
		data = input.getList(self.options.data_file)
		features = input.getFeatures(self.options.feature_file)
		multiphones = input.getMultiphones(self.options.phone_file)
		analysis = Analysis()
		analysis.readData(data, multiphones)

		output = Output()


		if self.options.min_pairs:
			display = analysis.findMinPairs()		
		elif self.options.environs:
			display = output.getEnvirons(analysis.environhash, features, self.options.verbose, self.options.words)
		elif self.options.export_tabs or self.options.export_commas:
			delim_char = '\t'
			if self.options.export_commas:
				delim_char = ','
			display = output.getPhones(analysis.phonehash, features, self.options.verbose, self.options.words, delim_char)
		elif self.options.distributions:
			display = analysis.findDistributions()
		else:
			display = output.getFormattedPhones(analysis.phonehash, features, self.options.verbose, self.options.words)

#		f = codecs.open('apecresults', 'w', 'utf-8')
#		f.write(display)
		print(display)

class Input:
	"""
	Prepares data for analysis
	"""

	# QuantHistLing
	# convenience method for iterating over hash and printing
	def printHash(self, hash):
		for k, v in hash.items():
			print(k, "\t", v)

	# QuantHistLing
	# calculate diphtong frequency counts
	def calculateDiphthongFrequency(self, diphthong_count, diphthong_unique_list):
		sorted_diphthong_counts = sorted(diphthong_unique_list.items(), key=operator.itemgetter(1), reverse=True)
		# print sorted_diphthong_counts
		print
		for i in sorted_diphthong_counts:
			freq = int(i[1]) / float(diphthong_count)
			print(i[0], "\t", i[1], "\t", freq)

	# QuantHistLing
	# method for getting unique list of segments
	def getUniqueSegments(self, infile):
		unique_segments = {}
		file = open(infile, "r")
		line_count = 0
		char_count = 0
		
		for line in file:
			line_count += 1
			line = line.strip()

			for c in line:
				char_count += 1
				# print(c)
				if not c in unique_segments:
					unique_segments[c] = 1
				else:
					unique_segments[c] += 1

		# print(line_count)
		# print(char_count)
		# print(unique_segments)
		# print()

		# for k, v in unique_segments.items():
		#	print(k, v)
		# print(len(unique_segments))

		sorted_unique_segments = sorted(unique_segments.items(), key=operator.itemgetter(1), reverse=True)
		for unique_segment in sorted_unique_segments:
			print(unique_segment)

	# QuantHistLing
	# method for checking for diphthongs
	def identifyThongs(self, infile, thongs_file):
		input_file = open(infile, "r")
		diphthongs_file = open(thongs_file, "r")

		# create a diphthong list
		diphthongs_list = []	
		for line in diphthongs_file:
			line = line.strip()
			diphthongs_list.append(line)

		# locate diphthongs in the data
		line_count = 0
		diphthong_count = 0		
		diphthong_unique_list = {}
		for line in input_file:
			line_count += 1
			line = line.strip()

			# identify diphtongs in the words
			for diphthong in diphthongs_list:
				if line.__contains__(diphthong):
					diphthong_count += 1
					print(diphthong, "\t", line)

					if not diphthong in diphthong_unique_list:
						diphthong_unique_list[diphthong] = 1
					else:
						diphthong_unique_list[diphthong] += 1
		print()
		print("(possible) diphthong count", diphthong_count)
		print()
		print("number of unique diphthongs: ", len(diphthong_unique_list))
		self.printHash(diphthong_unique_list)
		print()
		self.calculateDiphthongFrequency(diphthong_count, diphthong_unique_list)

	
	# read words from file; strip white space; add word boundary symbols; append to list
	def getList(self, infile):
		datalist = []
		f = open(infile, 'r')
		for line in f.read().splitlines():
			for form in line.split():
				form = form.strip()
				if form != '':
					form = '#'+form+'#'
					datalist.append(form)
		return datalist

	# read in feature table
	def getFeatures(self, feat_file):
		feat_table = {}
		f = open(feat_file, 'r')
		for line in f:
			(symbol, features) = line.strip().split('\t')
			feat_table[symbol] = features
		return feat_table


	# updated to get multiphones from an orthography profile
	def getMultiphones(self, phone_file):
		phone_table = {}
		f = open(phone_file, 'r')
		for line in f:
			# skip comments
			if line.startswith("#"):
				continue
			# deal with line comments
			if line.__contains__("#"):
				tokens = line.partition("#")
				line = tokens[0]
				
			line = line.strip()
			columns = line.split(",")
			phone = columns[-1].strip() # take the IPA column 
			print(phone)
			first = phone[0]
			if not first in phone_table:
				phone_table[first] = [phone]
			else:
				phone_table[first].append(phone)

		print("pt", phone_table)
		return phone_table




class Analysis:
	"""
	Finds phonetic environments for data
	"""
	
	def readData(self, datalist, multiphones):
		self.phonehash = {}
		self.environhash = {}

		# iterate over each word; get environments; populate hash from datalist; 
		# map each phone to table consisting of environemnts and their freqs 
		# .. in hash of hash

		# TODO: support multiple words per line; split on whitespace
		
		formslist = []
		for word in datalist:
			skip = 0
			form = []
			for i in range(0, len(word)):
				if (skip > 0):
					skip -= 1
					continue
				if word[i] in multiphones:
					multilist = multiphones[word[i]]
					found_entry = False
					for entry in multilist:
						if entry == word[i:i+len(entry)]:
							found_entry = True
							form.append(entry)
							skip = len(entry)-1
							break							
					if not found_entry:
						form.append(word[i])
				else:
					form.append(word[i])	
			formslist.append(form)
#		print(formslist)


		for form in formslist:
			for i in range(1, len(form)-1):
				initial = form[i-1]
				middle = form[i]
				final = form[i+1]
				environtuple = (initial, final)
				example = form[1:-1] # don't include word boundary tokens
			
				# add to phonehash				
				if not middle in self.phonehash:
					self.phonehash[middle] = {}
				if not environtuple in self.phonehash[middle]:
					self.phonehash[middle][environtuple] = []
				self.phonehash[middle][environtuple].append(example)
				
				# add to environhash; inverted version of phonehash
				if not environtuple in self.environhash:
					self.environhash[environtuple] = {}
				if not middle in self.environhash[environtuple]:
					self.environhash[environtuple][middle] = []
				self.environhash[environtuple][middle].append(example)


	def findDistributions(self):
		self.contrastive_pairs = []
		self.complementary_pairs = []
		
		phonelist = self.phonehash.keys()
		for i in range(len(phonelist)):
			phone1 = phonelist[i]
			for j in range(i+1, len(phonelist)):
				phone2 = phonelist[j]
				intersection = self.intersectingEnvironments(phone1, phone2)
				if len(intersection) > 0:
					self.contrastive_pairs.append((phone1, phone2))
				else:
					self.complementary_pairs.append((phone1, phone2))
					
		self.findMinPairs()
		contrastive_str = ''
		for pair in self.contrastive_pairs:
			minpair = ''
			if pair in self.minpair_hash:
				minpair = self.minpair_hash[pair]
			elif (pair[1], pair[0]) in self.minpair_hash: #.has_key((pair[1], pair[0])):
				minpair = self.minpair_hash[(pair[1], pair[0])]
			contrastive_str += str(pair) + '\t' + str(minpair) + '\n'
		return contrastive_str


	def intersectingEnvironments(self, phone1, phone2):
		environs1 = self.phonehash[phone1]
		environs2 = self.phonehash[phone2]
		intersection = []
		
		for e in environs1:
			for e2 in environs2:
				if e == e2 or (e[1],e[0]) == (e2[1],e2[0]):
#					print('ENVIRONS: '+str(e)+' '+str(e2))
					intersection.append(e)
#		print(phone1+','+phone2+': ',)
#		print(intersection)
		return intersection

	def findMinPairs(self):
		self.minpair_hash = {}

		outputstr = ''
		
		for environ in self.environhash:
			phonelist = self.environhash[environ].keys()
			phonelist = list(phonelist) # flip to list - must be a change in Python 3 update
			for i in range(0, len(phonelist)):
				examples = self.environhash[environ][phonelist[i]]
				for e in range(0, len(examples)):
					example = examples[e]
					for j in range(i+1, len(phonelist)):
						examples2 = self.environhash[environ][phonelist[j]]
						for e2 in range(0, len(examples2)):
							if self.isMinPair(example, examples2[e2]):
								example = ''.join(example)
								example2 = ''.join(examples2[e2])
								phonepair = (phonelist[i], phonelist[j])
								self.minpair_hash[phonepair] = (example, example2)
								outputstr += phonelist[i]+','+phonelist[j]+' : '
								outputstr += example+','+example2+'\n'
		return outputstr

	def getMinPairsList(self):
		pairs_list = []
		
		for environ in self.environhash:
			phonelist = self.environhash[environ].keys()
			for i in range(0, len(phonelist)):
				examples = self.environhash[environ][phonelist[i]]
				for e in range(0, len(examples)):
					example = examples[e]
					for j in range(i+1, len(phonelist)):
						examples2 = self.environhash[environ][phonelist[j]]
						for e2 in range(0, len(examples2)):
							if self.isMinPair(example, examples2[e2]):
								pairs_list.append(example)
								pairs_list.append(examples2[e2])

		return Output.toStrDisplay(Output(), pairs_list)

	def isMinPair(self, one, two):
		if (len(one) != len(two)):
			return False

		diff = 0
		for i in range(0, len(one)):
			if one[i] != two[i]:
				diff += 1

		if diff == 1:
			return True
		return False

	
class Output:
	"""
	Arranges data into various output formats
	"""
	def getFormattedPhones(self, phonehash, feat_table, verbose, words):
		output = ''
		for k in phonehash:
			k_str = verbose and k in feat_table and '['+feat_table[k]+']' or k
			output += k_str+'\n'+'---'+'\n'
			for e in phonehash[k]:
				left_str = verbose and e[0] in feat_table and '['+feat_table[e[0]]+'] ' or e[0]
				right_str = verbose and e[1] in feat_table and ' ['+feat_table[e[1]]+']' or e[1]
				examples = words and str(self.toStrList(phonehash[k][e])) or str(len(phonehash[k][e]))
				output += left_str+'_'+right_str+'   '+examples+'\n'
			output += '\n\n'
		# TODO
		# make sophisticated sorting algorithmics
		return output
	
	def getEnvirons(self, environhash, feat_table, verbose, words):
		output = ''
		for e in environhash:
			left_str = verbose and e[0] in feat_table and '['+feat_table[e[0]]+'] ' or e[0]
			right_str = verbose and e[1] in feat_table and ' ['+feat_table[e[1]]+']' or e[1]
			output += left_str+'_'+right_str+'\n'+'-------'+'\n'
			for p in environhash[e]:
				p_str = verbose and p in feat_table and '['+feat_table[p]+']' or p
				examples = words and str(self.toStrList(environhash[e][p])) or str(len(environhash[e][p]))
				output += p_str+'   '+examples+'\n'
			output += '\n\n'
		return output

	def getPhones(self, phonehash, feat_table, verbose, words, delim_char):

		phones_with_environs = []

		for p in phonehash:
			phone = verbose and p in feat_table and '['+feat_table[p]+']' or p

			for e in phonehash[p]:
				left_str = verbose and e[0] in feat_table and '['+feat_table[e[0]]+'] ' or e[0]
				
				right_str = verbose and e[1] in feat_table and ' ['+feat_table[e[1]]+']' or e[1]
				
				examples = words and str(self.toStrList(phonehash[p][e])) or str(len(phonehash[p][e]))

				phones_with_environs.append([phone, left_str+'_'+right_str, examples])

		return self.toDelimedFormat(phones_with_environs, delim_char)


	def toDelimedFormat(self, matrix, delim_char):

		output = ''
		
		for i in range(len(matrix)):
			for j in range(len(matrix[i])):
				output += matrix[i][j]
				if (j < len(matrix[i])-1):
					output += delim_char
			output += '\n'

		return output	


	def transpose(self, list_of_lists):
		
		for i in range(len(list_of_lists)):
			for j in range(len(list_of_lists[i])):
				if (j < len(list_of_lists[i])-1):
					newlist[i][j] = list_of_lists[j][i]

	def toStrList(self, list_of_lists):
		list_of_strings = []
		for list in list_of_lists:
			list_of_strings.append(''.join(list))
		return list_of_strings

	def toStrDisplay(self, list_of_lists):
		list_of_strings = self.toStrList(list_of_lists)
		output = ''
		for string in list_of_strings:
			if output != '':
				output += ', '
			output += string
		return '['+output+']'

if __name__=="__main__":
	main = Main()
	main.readFlags()
	main.findPhones()
	# main.getUniqueSegments()
	#main.identifyThongs()
