from urllib.parse import urlencode, quote
import urllib.request as urllib2
from urllib.error import HTTPError
collins_id = "x6fNbGx68bUMwfFTq6Uj1BGS2iEYnZXhTGJFklWFOusUrEgBxbbStmKVE2kRskL9"
import json, re
import very_general_functions as vgf
p = print

class API(object):

    def _getBaseUrl(self):
        return self._baseUrl

    def _setBaseUrl (self, baseUrl):
        if baseUrl and baseUrl[-1] != '/':
            self._baseUrl = baseUrl + '/'
        else:
            self._baseUrl = baseUrl

    baseUrl = property(_getBaseUrl, _setBaseUrl)

    def __init__(self, baseUrl, accessKey, userAgent = urllib2):
        self.baseUrl = baseUrl
        self.accessKey = accessKey
        self.userAgent = userAgent

    def _buildUrl(self, *pathParts, **queryParts):
        uri = self._baseUrl
        uri += "/".join([quote(p) for p in pathParts])

        nonNullQueryParts = {}
        for paramName, paramValue in queryParts.items():
            if paramValue is not None:
                nonNullQueryParts[paramName] = paramValue
        if nonNullQueryParts:
            uri +=  "?%s" % urlencode(nonNullQueryParts)
        return uri

    def _open(self, url):
        request = self._prepareGetRequest(url)
        response = self.userAgent.urlopen(request)
        body = response.read()
        return body

    def _prepareGetRequest(self, url):
        request = self.userAgent.Request(url)
        request.add_header('accessKey', self.accessKey)
        return request

    def getDictionaries(self):
        url = self._buildUrl('dictionaries')
        return self._open(url)

    def getDictionary(self, dictionaryCode):
        url = self._buildUrl('dictionaries', dictionaryCode)
        return self._open(url)

    def getEntry (self, dictionaryCode, entryId, entryFormat=None):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'entries',
                              entryId,
                              format=entryFormat)
        return self._open(url)

    def getEntryPronunciations (self, dictionaryCode, entryId, lang):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'entries',
                              entryId,
                              'pronunciations',
                              lang=lang)
        return self._open(url)

    def getNearbyEntries (self, dictionaryCode, entryId, entryNumber=None):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'entries',
                              entryId,
                              'nearbyentries',
                              entrynumber=entryNumber)
        return self._open(url)

    def getRelatedEntries (self, dictionaryCode, entryId):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'entries',
                              entryId,
                              'relatedentries')
        return self._open(url)

    def getWordOfTheDay(self, dictionaryCode=None, day=None, entryFormat=None):
        params = dict(day=day, format=entryFormat)
        url = None
        if dictionaryCode is not None:
            url = self._buildUrl('dictionaries',
                                  dictionaryCode,
                                  'wordoftheday',
                                  **params)
        else:
            url = self._buildUrl('wordoftheday',
                                 **params)
        return self._open(url)

    def getWordOfTheDayPreview(self, dictionaryCode=None, day=None):
        params = dict(day=day)
        url = None
        if dictionaryCode is not None:
            url = self._buildUrl('dictionaries',
                                  dictionaryCode,
                                  'wordoftheday',
                                  'preview',
                                  **params)
        else:
            url = self._buildUrl('wordoftheday',
                                  'preview',
                                  **params)
        return self._open(url)

    def search(self, dictionaryCode, searchWord, pageSize=None, pageIndex=None) :
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'search',
                              q=searchWord,
                              pagesize=pageSize,
                              pageindex=pageIndex)
        return self._open(url)

    def searchFirst (self, dictionaryCode, searchWord, entryFormat=None):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'search',
                              'first',
                              q=searchWord,
                              format=entryFormat)
        return self._open(url)

    def didYouMean(self, dictionaryCode, searchWord, entryNumber=None):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'search',
                              'didyoumean',
                              q=searchWord,
                              entrynumber=entryNumber)
        return self._open(url)

    def getThesaurusList(self, dictionaryCode):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'topics')
        return self._open(url)

    def getTopic (self, dictionaryCode, thesName, topicId):
        url = self._buildUrl('dictionaries',
                              dictionaryCode,
                              'topics',
                              thesName,
                              topicId)
        return self._open(url)


def use_did_you_mean(word, api):
    b = json.loads(api.didYouMean('german-english', word))
    for e, word in enumerate(b['suggestions']):
        p (e, word)

    str1 = input('choose suggestions, x for none: ')
    if str1 == 'x':
        return 0
    else:
        return b['suggestions'][int(str1)]




def get_entry(word, api, dct1={}, done=set()):
    b = json.loads(api.search('german-english', word))
    entries = []
    if not b['results']:
        p (f'no collins api entry for {word}')
        return []

    for e, v in enumerate(b['results']):
        entryid = v['entryId']
        lst = entryid.split('_')
        tword = lst[0]
        if not e:
            oword = tword

        if tword in dct1.keys():
            done.add(tword)
        elif not e or (e and tword == oword):
            try:
                c = json.loads(api.getEntry('german-english', entryid))
                str1 = c['entryContent']
                str2 = vgf.use_beautiful_soup(str1, 1, 1)
                str2 = str2.replace(chr(160), " ")
                lst1 = str2.split('  ')
                for e, x in enumerate(lst1):
                    x = re.sub(r'\[.+HTML5 audio\.\]','',x)
                    lst1[e] = x


                entry_word = lst1[0]
                if " " in entry_word:
                    entry_word = entry_word[:entry_word.index(" ")]
                if not entry_word in dct1 and entry_word not in done:
                    lst1.insert(0, entry_word)
                    entries += lst1
                else:
                    done.add(entry_word)

            except HTTPError:
                p (f'no entry for {word}')
            except:
                p (f'error in {word}')
        else:
            entries.append(f'#{tword}')

    if entries:
        entries.insert(0, '__collins_api__')

    return entries


def use_collins():
    url = "https://api.collinsdictionary.com/api/v1"
    return API(baseUrl=url, accessKey=collins_id, userAgent=urllib2)





