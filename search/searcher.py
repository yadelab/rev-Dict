import requests
import re
import queue
import sys

API_KEY = 'eb4e57bb2c34032da68dfeb3a0578b68'
URL_MASK = 'http://words.bighugelabs.com/api/2/{key}/{word}/'
ABBREVIATIONS = {
	'Synonym': 'syn',
	'Antonym': 'ant',
}
DELIMITER = ','

class Word(object):
    def __init__(self, priority, word):
        self.priority = priority
        self.word = word
        return
    def __lt__(self, other):
    	self_priority = self.priority
    	other_priority = other.priority
    	return self_priority > other_priority

def _lookup_word(word, relationship, begins_with, ends_with, searched_words):
	"""Looks up a word in the Big Huge Thesaurus and returns
	similar words that fit the parameters.
	:param word: word to look up
	:param relationship: relationship to entered word ('Synonym' or 'Antonym')
	:param begins_with: letters that the desired word starts with
	:param ends_with: letters that the desired word ends with
	:return: a list of similar words that match the requirements
	"""
	url = URL_MASK.format(key= API_KEY, word = word)
	r = requests.get(url)
	text = r.text.split('\n')
	
	relationship = ABBREVIATIONS[relationship]
	word_re = re.compile('^' + begins_with + '(.+)?' + ends_with + '$')

	found_words = []
	for group in text:
		s = group.split('|')
		if len(s) > 1:
			article, rel, synonym = s
			#Don't repeat words in the search entry
			if synonym in searched_words:
				continue

			if rel == relationship:
				if begins_with or ends_with:
					if word_re.search(synonym):
						found_words.append(synonym)
				else:
					found_words.append(synonym)

	return found_words

def _sort_by_frequency(all_words):
	"""Groups a list of list by their frequency.
	
	:param all_words: a list of lists with all words
	
	:return: a list of words as keys and their frequency as values.
	"""
	frequency_list = {}
	for group in all_words:
		for word in group:
			if not word in frequency_list:
				frequency_list[word] = 1
			else:
				frequency_list[word] += 1

	word_q = queue.PriorityQueue()

	for each_key in frequency_list:
		word_q.put( Word(frequency_list[each_key], each_key) )

	return word_q

def parse_search_entry(entry, relationship, begins_with = '', ends_with = '', num_words = sys.maxsize):
	"""Takes a search entry and returns the related words with the highest frequency.
	:param word: word to look up
	:param relationship: relationship to entered word ('Synonym' or 'Antonym')
	:param begins_with: letters that the desired word starts with
	:param ends_with: letters that the desired word ends with
	:param num_words: number of results to display

	:return: a string with all the related words separated by commas
	"""
	if not entry:
		return

	entry = entry.strip()
	words = entry.split(DELIMITER)
	all_related_words = []
	for word in words:
		word = word.strip()
		related_words = _lookup_word(word, relationship, begins_with, ends_with, words)
		all_related_words.append(related_words)

	results_queue = _sort_by_frequency(all_related_words)

	results_list = []
	for i in range(num_words):
		if results_queue.empty():
			break
		results_list.append(results_queue.get().word)
		
	results_list = sorted(results_list)
	return ', '.join(results_list)
