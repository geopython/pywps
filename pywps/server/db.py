import psycopg2 as postgresql


class DBPostgreSQL():
	def __init__(self, db_name, user, password):
		self.connect = postgresql.connect("dbname='{}' user='{}' password='{}'".format(db_name, user, password))
		self.cursor = self.connect.cursor()

	def __del__(self):
		self.connect.close()

	def execute(self, query):
		self.cursor.execute(query)

	def fetchone(self):
		return self.cursor.fetchone()

	def fetchall(self):
		return self.cursor.fetchall()