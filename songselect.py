import cookielib
import lxml.html
import urllib
import urllib2
import urlparse


class Connection(object):
    _BASE_URL = 'https://au.songselect.com'
    _LOGIN_URL = '/account/login'
    _LOGOUT_URL = '/account/logout'
    _USERNAME_FIELD = 'UserName'
    _PASSWORD_FIELD = 'Password'

    def __init__(self, cookies=None):
        self._cookiejar = cookielib.CookieJar()
        if cookies:
            for c in cookies:
                self._cookiejar.set_cookie(c)

        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookiejar))

    def _Fetch(self, path, data=None):
        if data is not None:
            data = urllib.urlencode(data)

        response = self._opener.open(
            urlparse.urljoin(self._BASE_URL, path),
            data=data)
        if response.getcode() != 200:
            raise IOError('Received HTTP code: {}'.format(response.code))

        return lxml.html.document_fromstring(response.read())

    def GetCookies(self):
        return list(self._cookiejar)

    def Login(self, user, password):
        form = [f for f in self._Fetch(self._LOGIN_URL).forms if
                self._LOGIN_URL in f.action and
                self._USERNAME_FIELD in f.inputs and
                self._PASSWORD_FIELD in f.inputs][0]
        values = dict(form.form_values())
        values[self._USERNAME_FIELD] = user
        values[self._PASSWORD_FIELD] = password
        page = self._Fetch(f.action, data=values)
        if page.find('.//a[@href="{}"]'.format(self._LOGOUT_URL)) is None:
            raise ValueError('Login credentials not accepted.')

    def Logout(self):
        self._Fetch(self._LOGOUT_URL)

    def _GetLines(self, element):
        return [t.strip() for t in element.itertext() if t.strip()]

    def _GetLyricsLink(self, overview):
        links = [e.attrib['href'] for e in overview.findall('.//a[@href]')]
        return [l for l in links if l.endswith('/viewlyrics')][0]

    def GetSong(self, songid):
        overview = self._Fetch('/songs/{}'.format(songid))
        lyrics = self._Fetch(self._GetLyricsLink(overview))
        title = overview.find('.//title').text
        section = lyrics.find('.//*[@class="lyrics"]')

        copyright_lines = []
        for elem in section.iterchildren():
            classes = set(elem.attrib.get('class', '').split())
            if classes.intersection(['authors', 'copyright']):
                copyright_lines.extend(self._GetLines(elem))

        lyric_sections = []
        lyric_state = ['', []]
        def EndSection():
            if lyric_state[1]:
                lyric_sections.append(tuple(lyric_state))
                lyric_state[1] = []

        for elem in section.iterchildren():
            if 'class' in elem.attrib: continue
            if elem.tag.startswith('h'):
                EndSection()
                lyric_state[0] = elem.text_content().strip()
            elif elem.tag == 'p':
                lyric_state[1].extend(self._GetLines(elem))

        EndSection()

        return {
            'sections': lyric_sections,
            'copyrightLines': copyright_lines,
            'title': lyrics.find('.//title').text,
        }
