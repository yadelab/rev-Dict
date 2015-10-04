import requests, re

API_KEY = 'eb4e57bb2c34032da68dfeb3a0578b68'
URL_MASK = 'http://words.bighugelabs.com/api/2/{key}/{word}/'
ABBREVIATIONS = {
	'Synonym': 'syn',
	'Antonym': 'ant',
}

def _lookup_word(word, relationship, begins_with, ends_with):
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
			if rel == relationship:
				if begins_with or ends_with:
					if word_re.search(synonym):
						found_words.append(synonym)
				else:
					found_words.append(synonym)

	return found_words

def _sort_by_frequency (all_words):
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

	return frequency_list
	
def _get_highest_frequency(frequency_list):
	"""Returns the highest frequency value in a list sorted by word frequency.

		:param frequency_list: a list of words and their corresponding frequency

		:return: the highest frequency value in the frequency_list
	"""
	highest = 0
	for frequency in frequency_list.values():
		if frequency > highest:
			highest = frequency

	return highest

def parse_search_entry(entry, relationship, begins_with = '', ends_with = ''):
	"""Takes a search entry and returns the related words with the highest frequency
	according to the search terms.

	:param word: word to look up
	:param relationship: relationship to entered word ('Synonym' or 'Antonym')
	:param begins_with: letters that the desired word starts with
	:param ends_with: letters that the desired word ends with

	:return: a list of the related words with the highest frequency
	"""
	entry = entry.strip()
	words = entry.split(' ')
	all_related_words = []
	for word in words:
		related_words = _lookup_word(word, relationship, begins_with, ends_with)
		all_related_words.append(related_words)

	words_by_frequency = _sort_by_frequency(all_related_words)
	highest_frequency = _get_highest_frequency(words_by_frequency)

	best_related_words = sorted([word for word, freq in words_by_frequency.items() if freq == highest_frequency])

	if len(best_related_words) < 10:
		return best_related_words
	else:
		return best_related_words[0:10]