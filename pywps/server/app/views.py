@self.application.route('/')
def hello_world():
	return "Hello PyWPS!"

@self.application.route('/wps')
def wps():
	return self.wps

@self.application.route('/user/<username>')
def show_user_profile(username):
	return 'User %s' % username