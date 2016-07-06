import cgi
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import urllib
from google.appengine.api import urlfetch


import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Tutorial(ndb.Model):
    title=ndb.StringProperty()
    description=ndb.StringProperty()
    abstract=ndb.StringProperty()
    author=ndb.StringProperty()

class UserData(ndb.Model):
    """Data Entry For Fest"""
    username = ndb.StringProperty()
    name = ndb.StringProperty()
    password=ndb.StringProperty()
    contactnum = ndb.StringProperty()
    email = ndb.StringProperty()
    educationdetails = ndb.StringProperty()

class UserTutorial(ndb.Model):
    userid = ndb.StringProperty()
    tutorialid = ndb.StringProperty()




class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('main.html')
        #self.response.set_cookie('user_id', result.user.id)
        self.response.write(template.render())
    def post(self):
        u=UserData()
        u.username=self.request.get('username')
        u.name=self.request.get('name')
        u.password=self.request.get('password')
        u.contactnum=self.request.get('contactnum')
        u.educationdetails=self.request.get('educationdetails')
        u.email=self.request.get('email')
        k=u.put()
        form_fields={
            "username": u.username,
            "password": u.password
        }
        #form_data = urllib.urlencode(form_fields)
        #url=self.request.url+"/HomePage"
        #result = urlfetch.fetch(url=url,payload=form_data,method=urlfetch.POST,headers={'Content-Type': 'application/x-www-form-urlencoded'})
        #self.redirect("/HomePage")
        template_values={'key': k}
        template = JINJA_ENVIRONMENT.get_template('submitted.html')
        self.response.write(template.render(template_values))

class HomePage(webapp2.RequestHandler):
    def get(self):
        uk=self.request.cookies.get('user_key')
        if len(uk)!=0:
            usr=ndb.Key('UserData',int(uk)).get()
            template_values={'username': usr.username,'key':usr.key}
            template = JINJA_ENVIRONMENT.get_template('home.html')
            self.response.set_cookie('user_key', str(usr.key.id()))
            self.response.write(template.render(template_values))
        else:
            self.redirect("/")

    def post(self):
        un=self.request.get('username')
        up=self.request.get('password')
        u_q=UserData.query(UserData.username==un).get()
        if u_q.password==up:
            template_values={'username': un,'key':u_q.key}
            template = JINJA_ENVIRONMENT.get_template('home.html')
            self.response.set_cookie('user_key', str(u_q.key.id()))
            self.response.write(template.render(template_values))
        else:
            self.response.out.write('wrong password! <a href="/">TryAgain</a>')

class AddTutorial(webapp2.RequestHandler):
    def get(self):
        uk=self.request.cookies.get('user_key')
        if len(uk)!=0:
            usr=ndb.Key('UserData',int(uk)).get()
            template_values={'username': usr.username,'key':usr.key}
            template = JINJA_ENVIRONMENT.get_template('addtutorial.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect("/")
            return
    def post(self):
        t=Tutorial()
        t.title=self.request.get('title')
        t.description=self.request.get('description')
        t.abstract=self.request.get('abstract')
        t.author=self.request.cookies.get('user_key')
        t.put()
        self.response.write("Successfuly put the Tutorial")
        self.redirect("HomePage")

class ListTutorial(webapp2.RequestHandler):
    def get(self):
        uk=self.request.cookies.get('user_key')
        if len(uk)!=0:
            usr=ndb.Key('UserData',int(uk)).get()
        else:
            self.redirect("/")
            return
        tutorials_query=Tutorial.query().order(Tutorial.title)
        tutorials=tutorials_query.fetch()
        template_values={'tutorials': tutorials, 'username': usr.username}
        template = JINJA_ENVIRONMENT.get_template('showAllTutorial.html')
        self.response.write(template.render(template_values))
    def post(self):
        self.response.write("post of lis tutorial, OOps.. wong Page!")

class JoinedTutorial(webapp2.RequestHandler):
    def get(self):
        uk=self.request.cookies.get('user_key')
        if len(uk)!=0:
            usr=ndb.Key('UserData',int(uk)).get()
        else:
            self.redirect("/")
        tutorials_query=UserTutorial.query(UserTutorial.userid == self.request.cookies.get('user_key'))
        tutorials=tutorials_query.fetch()
        display_tutorials=[]
        for t in tutorials:
            #self.response.write(t.tutorialid)
            tut=ndb.Key('Tutorial',int(t.tutorialid)).get()
            display_tutorials.append(tut)
            #self.response.write(str(tut.title)+str(tut.key))
        template_values={'tutorials': display_tutorials, 'username': usr.username }
        template = JINJA_ENVIRONMENT.get_template('showJoinedTutorial.html')
        self.response.write(template.render(template_values))
    def post(self):
        self.response.write("post of lis tutorial, OOps.. wong Page!")


class ViewTutorial(webapp2.RequestHandler):
    def get(self,tutorial_id):
        tut_qury = Tutorial.query(Tutorial.title == tutorial_id)
        tut=tut_qury.get()
        tutuser_query=UserTutorial.query(ndb.AND(UserTutorial.userid == self.request.cookies.get('user_key'), UserTutorial.tutorialid == str(tut.key.id())))
        tut_user=tutuser_query.fetch()
        if len(tut_user)>0:
            template_values={'tut': tut, 'joined': True}
        else:
            template_values={'tut': tut, 'joined': False}
        template = JINJA_ENVIRONMENT.get_template('tutorialpage2.html')
        self.response.write(template.render(template_values))

    def post(self,tutorial_id):
        tut_qury = Tutorial.query(Tutorial.title == tutorial_id)
        tut=tut_qury.get()
        ut=UserTutorial()
        ut.tutorialid=str(tut.key.id())
        ut.userid=self.request.cookies.get('user_key')
        k=ut.put()
        template_values={'tut': tut, 'joined': True}
        template = JINJA_ENVIRONMENT.get_template('tutorialpage2.html')
        self.response.write(template.render(template_values))

class LogOut(webapp2.RequestHandler):
    def get(self):
        self.response.set_cookie('user_key', "")
        self.response.write("logged out")
        self.redirect("/")
app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/HomePage', HomePage),
	('/AddTutorial', AddTutorial),
    ('/ListTutorial', ListTutorial),
    ('/JoinedTutorial', JoinedTutorial),
    ('/ViewTutorial/(.*)',ViewTutorial),
    ('/LogOut',LogOut)
	#('/Submit',SubmitNuForm),
	#('/ShowAll',ShowAll),
], debug=True)
