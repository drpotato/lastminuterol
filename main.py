#!/usr/bin/env python

import os
import pickle
import random

from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2

__author__ = 'Chris Morgan'

CHAIN_KEY = 'chain'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ROL(ndb.Model):
    text = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=False)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.jinja2')
        self.response.write(template.render({'rol': generate_rol()}))

    def post(self):
        rol = self.request.get('rol')
        if rol:
            text = '$BEGIN $NOW ' + rol + ' $END'
            new_rol = ROL(text=text)
            new_rol.put()
            memcache.delete(CHAIN_KEY)
        self.redirect('/submit')

    def old_post(self):
        attachments = self.request.POST.getall('attachments')

        for f in attachments:
            text = '$BEGIN $NOW ' + f.file.read() + ' $END'
            new_rol = ROL(text=text)
            new_rol.put()


class SubmissionHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('submit.jinja2')
        self.response.write(template.render())


class AdminViewHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('admin.jinja2')
        rols = ROL.query(ROL.approved == False)
        template_values = {
            'rols': list(rols)
        }
        self.response.write(template.render(template_values))


def generate_trigram(words):
    if len(words) < 3:
        return
    for i in xrange(len(words) - 2):
        yield (words[i], words[i+1], words[i+2])


def get_chain():
    chain = memcache.get(CHAIN_KEY)

    if chain:
        return pickle.loads(chain)
    else:
        chain = {}

    for rol in ROL.query(ROL.approved == True):
        words = rol.text.split()
        for word1, word2, word3 in generate_trigram(words):
            key = (word1, word2)
            if key in chain:
                chain[key].append(word3)
            else:
                chain[key] = [word3]

    memcache.set(CHAIN_KEY, pickle.dumps(chain))
    return chain


def generate_rol():
    new_rol = []
    word1 = '$BEGIN'
    word2 = '$NOW'

    chain = get_chain()

    while True:
        word1, word2 = word2, random.choice(chain[(word1, word2)])
        if word2 == '$END':
            break
        new_rol.append(word2)

    return ' '.join(new_rol)

app = webapp2.WSGIApplication([
    ('/submit', SubmissionHandler),
    ('/', MainHandler)
], debug=True)

admin = webapp2.WSGIApplication([
    ('/admin', AdminViewHandler)
], debug=True)