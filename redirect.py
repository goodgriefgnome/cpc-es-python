import urlparse
import webapp2

import properties


def Redirector(mangle_url):
  class Handler(webapp2.RequestHandler):
    def dispatch(self):
      return self.redirect(code=307,
                           uri=mangle_url(self.request.url))

  return webapp2.WSGIApplication([('.*', Handler)])

def AsRelative(url):
  parts = list(urlparse.urlsplit(url))
  parts[0] = ''
  parts[1] = ''
  parts[2] = parts[2][1:]
  return urlparse.urlunsplit(parts)

to_java = Redirector(lambda url: urlparse.urljoin(
    'https://cpc-es-java.appspot.com/', AsRelative(url)))


def AsWisprepUrl(url):
  parts = urlparse.urlsplit(url)
  
  q = [p for p in parts.query.split('&') if p]
  q.append('f={}'.format(parts.path.split('/')[2]))
  return properties.Get('wisprep_url') + '?' + '&'.join(q)

to_wisprep = Redirector(AsWisprepUrl)
