import psycopg2
import pandas as pd

class Database:
	def __init__(self, dbname, user, password, host):
		self.conn = psycopg2.connect(dbname=dbname, user=user,
                        password=password, host=host)
		self.cursor = self.conn.cursor()

	def create_tables(self):
		with self.conn:
			self.cursor.execute("\
				CREATE TABLE users(\
					user_id varchar(30) PRIMARY KEY,\
					team_name varchar(30),\
					name varchar(30),\
					surname varchar(30),\
					fathername varchar(30),\
					role integer,\
					personal_task text,\
					action integer DEFAULT 0);")

			self.cursor.execute("\
				CREATE TABLE teams(\
					team_id serial PRIMARY KEY,\
					role1 varchar(30) REFERENCES users(user_id),\
					role2 varchar(30) REFERENCES users(user_id),\
					role3 varchar(30) REFERENCES users(user_id),\
					role4 varchar(30) REFERENCES users(user_id),\
					team_name varchar(30),\
					task1 text,\
					task2 text);")

			self.cursor.execute("\
				CREATE TABLE lottery(\
					lottery_id serial PRIMARY KEY,\
					user_id varchar(30) REFERENCES users(user_id),\
					task integer);")

			self.cursor.execute("\
				CREATE TABLE lottery_tasks(\
					task_id serial PRIMARY KEY,\
					task_text text,\
					task_answer integer)")

	def insert_lottery_tasks(self):
		with self.conn:
			self.cursor.execute("\
					   INSERT INTO lottery_tasks (task_id, task_text, task_answer)\
					   VALUES (1, 'Крупнейшая платформа для добрых дел – сайт «ФГАИС Молодежь России»?', 0)")
			self.cursor.execute("\
					   INSERT INTO lottery_tasks (task_id, task_text, task_answer)\
					   VALUES (2, 'Самая известная военно-спортивная игра пионеров называлась «Заря»', 0)")
			self.cursor.execute("\
					   INSERT INTO lottery_tasks (task_id, task_text, task_answer)\
					   VALUES (3, 'Российское движение детей и молодежи «Движение первых» было создано 14 июля 2021 года?', 0)")
			self.cursor.execute("\
					   INSERT INTO lottery_tasks (task_id, task_text, task_answer)\
					   VALUES (4, 'Областному центру «Содружество» в 2024 году исполнится 30 лет?', 1)")
			self.cursor.execute("\
					   INSERT INTO lottery_tasks (task_id, task_text, task_answer)\
					   VALUES (5, 'Три конца пионерского галстука символизируют нерушимую связь пионеров и государства?', 0)")
			self.cursor.execute("\
					   INSERT INTO lottery_tasks (task_id, task_text, task_answer)\
					   VALUES (6, 'Федеральный закон № 82-ФЗ «Об общественных объединениях» был принят 19 мая 1995 года?', 0)")

	def clear_table(self, table_name):
		with self.conn:
			self.cursor.execute(f"DELETE FROM {table_name}")

	def get_users_exel(self):
		script = (f"SELECT team_name as Команда, surname as Фамилия, name as Имя, fathername as Отчество FROM users ORDER BY team_name")
		df = pd.read_sql_query(script, self.conn)

		writer = pd.ExcelWriter(f'users.xlsx')
		df.to_excel(writer, sheet_name='bar')
		writer._save()


	def get_table(self, table_name):
		script = f"SELECT * FROM {table_name}"
		df = pd.read_sql_query(script, self.conn)

		writer = pd.ExcelWriter(f'{table_name}.xlsx')
		df.to_excel(writer, sheet_name='bar')
		writer._save()

	def get_task1_table(self):
		script = f"SELECT team_name AS Команда, task1 AS Визитка FROM teams"
		df = pd.read_sql_query(script, self.conn)

		writer = pd.ExcelWriter(f'tasks1.xlsx')
		df.to_excel(writer, sheet_name='bar')
		writer._save()

	def get_task2_table(self):
		script = f"SELECT team_name AS Команда, task2 AS Дело_дня FROM teams"
		df = pd.read_sql_query(script, self.conn)

		writer = pd.ExcelWriter(f'tasks2.xlsx')
		df.to_excel(writer, sheet_name='bar')
		writer._save()

	def get_personal_task_table(self):
		script = f"SELECT team_name AS Команда,\
			surname AS Фамилия,\
			name AS Имя,\
			fathername AS Отчество,\
			CASE role\
			WHEN 1 THEN 'Капитан'\
			WHEN 2 THEN 'Помощник капитана'\
			WHEN 3 THEN 'Штурман'\
			WHEN 4 THEN 'Механик'\
			END AS Роль,\
			personal_task AS Задание\
			FROM users ORDER BY team_name"
		df = pd.read_sql_query(script, self.conn)

		writer = pd.ExcelWriter(f'personal_tasks.xlsx')
		df.to_excel(writer, sheet_name='bar')
		writer._save()

	def get_lottery_table(self):
		script = f"SELECT lottery.lottery_id as Номер_ответа, users.surname as Фамилия, users.name as Имя, users.fathername as Отчество\
			  FROM users, lottery WHERE users.user_id=lottery.user_id ORDER BY users.surname"
		df = pd.read_sql_query(script, self.conn)

		writer = pd.ExcelWriter(f'Участники лотереи.xlsx')
		df.to_excel(writer, sheet_name='bar')
		writer._save()

	def get_tasks_info(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("SELECT role1, task1, task2 FROM teams")
			res = cursor.fetchall()
			return res
		except:
			pass
		finally:
			cursor.close()

	def get_action(self, user_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT action FROM users WHERE user_id='{user_id}'")
			res = cursor.fetchone()[0]
			return res
		except:
			pass
		finally:
			cursor.close()

	def set_action(self, user_id, action):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"UPDATE users SET action = {action} WHERE user_id = '{user_id}'")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def user_exist(self, user_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT * FROM users WHERE user_id='{user_id}'")
			return bool(len(cursor.fetchone()))
		except:
			pass
		finally:
			cursor.close()

	def get_ids(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT user_id FROM users")
			return cursor.fetchall()
		except:
			pass
		finally:
			cursor.close()

	def team_exist(self, team_name):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT * FROM teams WHERE team_name='{team_name}'")
			return bool(len(cursor.fetchone()))
		except:
			pass
		finally:
			cursor.close()

	def add_team(self, team_name):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"INSERT INTO teams (team_name) VALUES ('{team_name}')")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def get_team_by_user_id(self, user_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT team_name FROM users WHERE user_id = '{user_id}'")
			return cursor.fetchone()[0]
		except:
			pass
		finally:
			cursor.close()

	def add_user(self, user_id, team_name, name, surname, fathername, role):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"INSERT INTO users (user_id, team_name, name, \
				surname, fathername, role) VALUES ('{user_id}', '{team_name}', '{name}', '{surname}', '{fathername}', {role})")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def add_role(self, user_id, team_name, role):
		try:
			cursor = self.conn.cursor()
			roleDict = {
			1: 'role1',
			2: 'role2',
			3: 'role3',
			4: 'role4'
			}
			cursor.execute(f"UPDATE teams  SET {roleDict[role]} = '{user_id}' WHERE team_name = '{team_name}'")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def get_role(self, user_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT role FROM users WHERE user_id = '{user_id}'")
			return cursor.fetchone()[0]
		except:
			pass
		finally:
			cursor.close()

	def check_team_task(self, team_name, task):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT {task} FROM teams WHERE team_name = '{team_name}'")
			return cursor.fetchone()
		except:
			pass
		finally:
			cursor.close()

	def check_personal_task(self, user_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT personal_task FROM users WHERE user_id = '{user_id}'")
			return cursor.fetchone()
		except:
			pass
		finally:
			cursor.close()

	def make_team_task(self, team_name, task, task_text):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"UPDATE teams SET {task} = '{task_text}' WHERE team_name = '{team_name}'")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def make_personal_task(self, user_id, task_text):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"UPDATE users SET personal_task = '{task_text}' WHERE user_id = '{user_id}'")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def add_lottery(self, user_id, task):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"INSERT INTO lottery (user_id, task) VALUES ('{user_id}', {task})")
			self.conn.commit()
		except:
			pass
		finally:
			cursor.close()

	def get_lottery_text(self, task_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT task_text FROM lottery_tasks WHERE task_id={task_id}")
			return cursor.fetchone()[0]
		except:
			pass
		finally:
			cursor.close()

	def check_lottery(self, task_text, task_answer):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT * FROM lottery_tasks WHERE task_text='{task_text}' AND task_answer={task_answer}")
			res = cursor.fetchone()
			return bool(res)
		except:
			pass
		finally:
			cursor.close()

	def get_lottery(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT * FROM lottery")
			res = cursor.fetchall()
			return res
		except:
			pass
		finally:
			cursor.close()

	def get_FIO(self, user_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute(f"SELECT surname, name, fathername FROM users WHERE user_id='{user_id}'")
			res = cursor.fetchone()
			return res
		except:
			pass
		finally:
			cursor.close()

if __name__ == '__main__':
	pass
