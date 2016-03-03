from requests.adapters import HTTPAdapter
from requests_futures.sessions import FuturesSession
from pprint import pprint
import re

class FXRevision(object):

    ARCHIVES_URL = 'http://archive.mozilla.org'
    NIGHTLY_URL = ARCHIVES_URL + '/pub/firefox/nightly/'
    TIMEOUT = 5
    MAX_RETRIES = 5

    def __init__(self, versions, fx_version, os):
        self.results = [ ]
        self.dates = { }
        self.fx_version = fx_version
        self.os = os
        self.info = { }
        pattern = re.compile('([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})')
        for version in versions:
            m = pattern.search(version)
            self.dates[version] = [m.group(i) for i in range(1, 7)]

        self.session = FuturesSession()
        self.session.mount(self.ARCHIVES_URL, HTTPAdapter(max_retries = self.MAX_RETRIES))
        self.__get_info()

    def get(self):
        for r in self.results:
            r.result()
        return self.info
        
    def __make_url(self, l):
        return self.NIGHTLY_URL + l[0] + '/' + l[1] + '/' + '-'.join(l) + '-mozilla-central/firefox-' + self.fx_version + '.en-US.' + self.os + '.json'

    def __info_cb(self, sess, res):
        json = res.json()
        self.info[json['buildid']] = json['moz_source_stamp']
    
    def __get_info(self):
        for date in self.dates.itervalues():
            self.results.append(self.session.get(self.__make_url(date),
                                                 timeout = self.TIMEOUT,
                                                 background_callback = self.__info_cb))

#fxr = FXRevision(['20160223030304'], '47.0a1', 'linux-i686')
#pprint(fxr.get())
            
#    2016/02/2016-02-23-03-03-04-mozilla-central/firefox-47.0a1.en-US.linux-i686.txt'