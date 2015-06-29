"""A simple webapp2 server."""

import webapp2


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('SPARQL')


application = webapp2.WSGIApplication([
    ('/sparql', MainPage),
], debug=True)
