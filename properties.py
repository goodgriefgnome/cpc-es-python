import webapp2
from google.appengine.ext import ndb

class Properties(ndb.Model):
  value = ndb.BlobProperty()

  @staticmethod
  def MakeKey(key):
    return ndb.Key(Properties, key)

def Get(key):
  return Properties.MakeKey(key).get().value


class SetProperty(webapp2.RequestHandler):
  def get(self):
    p = Properties(id=self.request.get('key'),
                   value=self.request.get('value'))
    p.put()


app = webapp2.WSGIApplication([
  ('/admin/properties/set', SetProperty),
])
