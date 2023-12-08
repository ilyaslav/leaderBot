import telebot
from telebot import types
import datetime
import time
import threading
import schedule
import random
import config

from database import Database

bot = telebot.TeleBot(config.bot_token)
db = Database(config.db_name, config.db_user, config.db_password, config.db_addr)

@bot.message_handler(commands=['start'])
def start(message):
	reg_dt = datetime.datetime(2023,11,29,0,0)
	image = open('img/hi.png',  'rb')
	if datetime.datetime.today() < reg_dt and not db.user_exist(message.chat.id):
		markupReply = types.ReplyKeyboardMarkup(resize_keyboard = True)
		item_reg = types.KeyboardButton('Регистрация')
		item_help = types.KeyboardButton('Поддержка')
		markupReply.add(item_reg)
		markupReply.add(item_help)
		bot.send_photo(message.chat.id, photo = image, reply_markup=markupReply, caption = \
f"Приветствую участников космического путешествия!\n\n\
Меня зовут КомЛид, я пришелец из другой галактики. Буду рад \
познакомиться со всеми вами! Давайте начнем наше путешествие!\n\n\
При регистрации не забудьте указать вашу роль в экипаже: капитан, \
помощник капитана, штурман, механик.\n\n\
Стартуем прямо СЕЙЧАС! 🚀🚀🚀")
	elif db.user_exist(message.chat.id):
		bot.send_photo(message.chat.id, photo = image, caption = \
f"Меня зовут КомЛид! Я буду вашим проводником в этом путешествии!")

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
	if call.data == 'yes':
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=types.InlineKeyboardMarkup([]))
		lot_id = db.check_lottery(call.message.caption, 1)
		if lot_id:
			db.add_lottery(call.message.chat.id, int(lot_id))
		mes_text = 'Ответ принят!'
		bot.send_message(text=mes_text, chat_id=call.message.chat.id, parse_mode="html")


	elif call.data == 'no':
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=types.InlineKeyboardMarkup([]))
		lot_id = db.check_lottery(call.message.caption, 0)
		if lot_id:
			db.add_lottery(call.message.chat.id, lot_id)
		mes_text = 'Ответ принят!'
		bot.send_message(text=mes_text, chat_id=call.message.chat.id, parse_mode="html")


@bot.message_handler(content_types="text")
def text_answer(message):
	if message.text == "Регистрация":
		if db.user_exist(message.chat.id):
			bot.send_message(text = f"Вы уже зарегистрированы!", chat_id=message.chat.id,  parse_mode="html")
		else:
			bot.send_message(text = f"Введите ФИО, команду и вашу роль в команде в формате: Фамилия,Имя,Отчество,Название команды,роль в команде\n\n\
Например: Иванов,Иван,Иванович,Команда лидеров,капитан", chat_id=message.chat.id,  parse_mode="html")

	elif message.text == "Поддержка":
		bot.send_message(chat_id=message.chat.id, text='@ilyadlav')
		db.set_action(message.chat.id ,0)

	elif message.text == "Визитка":
		db.set_action(message.chat.id, 1)
		bot.send_message(text = f"Введите ссылку на пост!", chat_id=message.chat.id,  parse_mode="html")

	elif message.text == "Дело дня":
		db.set_action(message.chat.id, 2)
		bot.send_message(text = f"Введите ссылку на видео!", chat_id=message.chat.id,  parse_mode="html")

	elif message.text == "Тематическое задание":
		db.set_action(message.chat.id ,3)
		bot.send_message(text = f"Введите текст или ссылку на видео!", chat_id=message.chat.id,  parse_mode="html")

	elif db.get_action(message.chat.id) == 1:
		bot.send_message(message.chat.id, f"Задание принято! В случае необходимости, вы можете отправить задание повторно!", parse_mode="html")
		team_name = db.get_team_by_user_id(message.chat.id)
		db.make_team_task(team_name, 'task1', message.text)
		db.set_action(message.chat.id ,0)

	elif db.get_action(message.chat.id) == 2:
		bot.send_message(message.chat.id, f"Задание принято! В случае необходимости, вы можете отправить задание повторно!", parse_mode="html")
		team_name = db.get_team_by_user_id(message.chat.id)
		db.make_team_task(team_name, 'task2', message.text)
		db.set_action(message.chat.id ,0)

	elif db.get_action(message.chat.id) == 3:
		bot.send_message(message.chat.id, f"Задание принято! В случае необходимости, вы можете отправить задание повторно!", parse_mode="html")
		db.make_personal_task(message.chat.id ,message.text)
		db.set_action(message.chat.id ,0)

	elif not db.user_exist(message.chat.id):
		register_user(message)

def register_user(message):
	data = message.text.split(',')
	if len(data) == 5:
		for i in range(5):
			data[i] = data[i].strip()
		if not db.team_exist(data[3]):
			if data[4].lower() == 'капитан':
				db.add_team(data[3])
				role = calculate_role(data[4])
				if role:
					db.add_user(message.chat.id, data[3], data[1], data[0], data[2], role)
					db.add_role(message.chat.id, data[3], role)

					markupReply = types.ReplyKeyboardMarkup(resize_keyboard = True)
					item_1 = types.KeyboardButton('Визитка')
					item_2 = types.KeyboardButton('Дело дня')
					item_help = types.KeyboardButton('Поддержка')
					markupReply.add(item_1)
					markupReply.add(item_2)
					markupReply.add(item_help)
					bot.send_message(message.chat.id, f"Вы успешно зарегистрировались!", reply_markup=markupReply, parse_mode="html")
				else:
					bot.send_message(message.chat.id, f"Неправильный формат роли в команде!", parse_mode="html")
			else:
				bot.send_message(message.chat.id, f"Команда не зарегистрирована! \
Для регистрации остальных участников команды сначала должен зарегистрироваться капитан!", parse_mode="html")

		else:
			role = calculate_role(data[4])
			if role:
				db.add_user(message.chat.id, data[3], data[1], data[0], data[2], role)
				db.add_role(message.chat.id, data[3], role)

				markupReply = types.ReplyKeyboardMarkup(resize_keyboard = True)
				item_1 = types.KeyboardButton('Визитка')
				item_2 = types.KeyboardButton('Дело дня')
				item_help = types.KeyboardButton('Поддержка')
				markupReply.add(item_1)
				markupReply.add(item_2)
				markupReply.add(item_help)
				bot.send_message(message.chat.id, f"Вы успешно зарегистрировались!", reply_markup=markupReply, parse_mode="html")
			else:
				bot.send_message(message.chat.id, f"Неправильный формат роли в команде!", parse_mode="html")
	else:
		bot.send_message(message.chat.id, f"Неправильный формат ввода данных!\
Введите ФИО, команду и вашу роль в команде в формате: Фамилия,Имя,Отчество,Название команды,роль в команде\n\n\
Например: Иванов,Иван,Иванович,Лидеры,капитан", parse_mode="html")

def calculate_role(role):
	if role == 'капитан':
		return 1
	elif role == 'помощник капитана':
		return 2
	elif role == 'штурман':
		return 3
	elif role == 'механик':
		return 4
	return 0

def send_scheduled_message():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		bot.send_message(chat_id=chat_id[0], text='text')

def scheduled_loop():
	while True:
		try:
			schedule.run_pending()
			time.sleep(1)
		except Exception as e:
			print(e)

def set_scheduled_list():
	schedule.every().wednesday.at("07:00").do(send_day1_message1)
	schedule.every().wednesday.at("11:00").do(send_day1_message2)
	schedule.every().wednesday.at("18:00").do(send_day1_message3)
	schedule.every().thursday.at("07:00").do(send_day2_message1)
	schedule.every().thursday.at("11:00").do(send_day2_message2)
	schedule.every().thursday.at("18:00").do(send_day2_message3)
	schedule.every().friday.at("07:00").do(send_day3_message1)
	schedule.every().friday.at("11:00").do(send_day3_message2)
	schedule.every().friday.at("18:00").do(send_day3_message3)
	schedule.every().saturday.at("07:00").do(send_day4_message1)
	schedule.every().saturday.at("11:00").do(send_day4_message2)
	schedule.every().saturday.at("18:00").do(send_day4_message3)
	schedule.every().sunday.at("07:00").do(send_day5_message1)
	schedule.every().sunday.at("11:00").do(send_day5_message2)
	schedule.every().sunday.at("15:00").do(send_answers)
	schedule.every().sunday.at("18:00").do(send_day5_message3)

	schedule.every().tuesday.at("17:00").do(send_lottery_message, 1)
	schedule.every().wednesday.at("12:00").do(send_lottery_message, 2)
	schedule.every().thursday.at("16:00").do(send_lottery_message, 3)
	schedule.every().friday.at("10:30").do(send_lottery_message, 4)
	schedule.every().saturday.at("13:10").do(send_lottery_message, 5)
	schedule.every().sunday.at("10:20").do(send_lottery_message, 6)
	schedule.every().sunday.at("11:55").do(send_answers_table)
	schedule.every().sunday.at("12:05").do(send_end_of_lottery)

	schedule.every().wednesday.at("06:45").do(send_captain_message)
	schedule.every().thursday.at("06:30").do(send_assistant_message)
	schedule.every().friday.at("06:30").do(send_navigator_message)
	schedule.every().saturday.at("06:30").do(send_mechanic_message)

def send_answers():
	data = db.get_tasks_info()
	for team in data:
		try:
			bot.send_photo(chat_id=team[0], photo=open('img/hi0.png',  'rb'), caption=\
				 f"Привет, капитан! Скоро выйдет время на отправку ответов! Проверь, тот ли ответ отправила ваша команда!\n\n\
Визитка: {team[1]}\n\
Дело дня: {team[2]}\n\n\
Для того, чтобы изменить ответ, нажми на кнопку соответствующего задания и отправь его заного!")
		except:
			pass

def send_answers_table():
	chat_ids = db.get_ids()
	db.get_lottery_table()
	for chat_id in chat_ids:
		try:
			with open('Участники лотереи.xlsx', 'rb') as f:
				bot.send_document(chat_id[0], caption='Таблица участников, которые правильно отвечали на вопросы лотереи. Чем больше раз ваша фамилия встретилась в таблице, тем выше шанс выигрыша!', document=f)
		except:
			pass

def send_document():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		with open('Задания.docx', 'rb') as f:
			to_pin = bot.send_document(chat_id[0], caption='Добрый вечер, земляне! Задания и критерии к ним вы найдете в прикрепленном документе.', document=f).message_id
		bot.pin_chat_message(chat_id[0], message_id = to_pin)

def send_day1_message1():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi.png',  'rb'), caption=\
				 """Доброе утро, земляне!
Вы уже приступили к выполнению заданий? Если еще нет, то скорее приступайте, потому что дальше вас ждет еще больше интересного!
Продуктивного дня!""")
		except:
			pass
	return schedule.CancelJob

def send_day1_message2():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Всем доброго дня!
Как у вас проходит день? У меня очень интересно!
Жду ваших ответов на задания, чтобы поближе познакомиться с вами!""")
		except:
			pass
	return schedule.CancelJob

def send_day1_message3():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый вечер, участники космического путешествия!
Надеюсь, ваш день прошел продуктивно! Не забывайте про розыгрыш.
Спокойной ночи!""")
		except:
			pass
	return schedule.CancelJob

def send_day2_message1():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi.png',  'rb'), caption=\
				 """Доброе утро!
Желаю всем вдохновения и сил на выполнение тематических заданий! """)
		except:
			pass
	return schedule.CancelJob

def send_day2_message2():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый день, земляне!
Сегодня я решил отправиться в путешествие по галактике. Было очень познавательно!
Надеюсь, ваш день проходить так же интересно, как и у меня! """)
		except:
			pass
	return schedule.CancelJob

def send_day2_message3():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый вечер!
Сегодня я узнал много нового о детских и молодежных общественных объединениях Вологодской области!
Было очень интересно! Спасибо! Увидимся завтра!""")
		except:
			pass
	return schedule.CancelJob

def send_day3_message1():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi.png',  'rb'), caption=\
				 """Доброе утро, земляне! Не забывайте выполнять задания. Хорошего дня!""")
		except:
			pass
	return schedule.CancelJob

def send_day3_message2():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый день!
Сегодня я решил познакомиться с земной литературой. Прочитал повесть «Тимур и его команда» А.П. Гайдара.

Было интересно читать! Даже захотел стать тимуровцем.
А вы читали эту повесть? Если нет, то обязательно прочитайте.""")
		except:
			pass
	return schedule.CancelJob

def send_day3_message3():
	chat_ids = db.get_ids()
	markupReply = types.ReplyKeyboardMarkup(resize_keyboard = True)
	item_1 = types.KeyboardButton('Визитка')
	item_2 = types.KeyboardButton('Дело дня')
	item_help = types.KeyboardButton('Поддержка')
	markupReply.add(item_1)
	markupReply.add(item_2)
	markupReply.add(item_help)
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), reply_markup=markupReply, caption=\
				 """Добрый вечер, земляне!
Сегодня был очень насыщенный день. Не забывайте выполнять задания.
Увидимся завтра!""")
		except:
			pass
	return schedule.CancelJob

def send_day4_message1():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi.png',  'rb'), caption=\
				 """Доброе утро, земляне!
Желаю вам, чтобы этот день прошел плодотворно!""")
		except:
			pass
	return schedule.CancelJob

def send_day4_message2():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый день всем!
Остались ли у вас задания, которые вы еще не выполнили?
Если да, то скорее выполняйте, потому что наше космическое путешествие подходит к концу.""")
		except:
			pass
	return schedule.CancelJob

def send_day4_message3():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый вечер!
Надеюсь, ваш день прошел продуктивно!
Не забывайте выполнять задания и участвовать в розыгрыше.""")
		except:
			pass
	return schedule.CancelJob

def send_day5_message1():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi.png',  'rb'), caption=\
				 """Доброе утро!
Сегодня последний день нашего путешествия. Активизируйте свои силы для выполнения оставшихся заданий.
Ответ на последний вопрос розыгрыша принимается сегодня до 14:00 час.""")
		except:
			pass
	return schedule.CancelJob

def send_day5_message2():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/hi0.png',  'rb'), caption=\
				 """Добрый день, земляне!
Ответы на задания конкурса принимаются сегодня до 22:00 час.
У вас еще есть время для сдачи заданий.""")
		except:
			pass
	return schedule.CancelJob

def send_day5_message3():
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/sad.png', 'rb'), caption=\
				 """Добрый вечер, земляне!

Я очень рад был узнать о том, какие детские и молодежные общественные объединения существуют на Земле.
Было интересно читать ваши ответы на тематические задания и на дополнительные задания.

Итоги конкурса публикуются 7 декабря 2023 года в группе «Лидеры Содружества» социальной сети ВКонтакте.
Спасибо всем за участие в областном конкурсе «Команда лидеров»! Желаю всем успехов!""")
		except:
			pass
	return schedule.CancelJob

def send_end_of_lottery():
	users_list = db.get_lottery()
	winer = random.choice(users_list)
	FIO = db.get_FIO(winer[1])
	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/nice.png',  'rb'), caption=\
				 f"Космический рандомайзер подвел итога розыгрыша!\nПобедителем стал(а) {FIO[0]} {FIO[1]} {FIO[2]}! Поздравляем!!!!\nОрганизаторы свяжутся с тобой.")
		except:
			pass
	return schedule.CancelJob


def send_lottery_message(number):
	chat_ids = db.get_ids()
	mes_text = db.get_lottery_text(number)

	markupInline = types.InlineKeyboardMarkup()
	itemTask1 = types.InlineKeyboardButton(text='Да', callback_data='yes')
	itemTask2 = types.InlineKeyboardButton(text='Нет', callback_data='no')
	markupInline.add(itemTask1)
	markupInline.add(itemTask2)

	for chat_id in chat_ids:
		print(chat_id[0])
		try:
			bot.send_photo(chat_id=chat_id[0], photo=open('img/why.png', 'rb'), reply_markup=markupInline,caption=mes_text)
		except:
			pass

	return schedule.CancelJob

def send_mechanic_message():
	mes_text = '''Добрый день, механики!

Мой механик недавно нашел решение внештатной ситуации прямо во время полета. Теперь мне хочется проверить механиков с Земли.

Я собрал для тебя несколько внештатных ситуаций. Тебе необходимо найти для них решения. Переходи по ссылке https://forms.yandex.ru/u/6564871a068ff095a1ee39c3/.
Жду выполнения задания 2 декабря с 10:00 до 21:00. Интересного дня!'''
	send_personal_message('img/why.png', mes_text, 4)
	return schedule.CancelJob

def send_navigator_message():
	mes_text = '''Добрый день, штурманы!

Я решил отправится в путешествие по вашей планете и побывать в местах, связанных с историей детского движения.

Приглашаю составить мне компанию в путешествии, переходи по ссылке https://forms.yandex.ru/u/65648012505690942be6c4bd/.
Жду выполнения задания 1 декабря с 10:00 до 21:00. Насыщенного дня!'''
	send_personal_message('img/why.png', mes_text, 3)
	return schedule.CancelJob

def send_assistant_message():
	mes_text = '''Добрый день, помощники капитанов!

Я очень хочу стать членом ДиМОО, но не могу выбрать объединение.

Чтобы помочь мне выбрать ДиМОО, перейдите по ссылке https://forms.yandex.ru/u/656479a8f47e738d1ba4bd80/.
Жду выполнения задания 30 ноября с 10:00 до 21:00. Продуктивного дня!'''
	send_personal_message('img/why.png', mes_text, 2)
	return schedule.CancelJob

def send_captain_message():
	mes_text = '''Добрый день, капитаны!

Сегодня я узнал, что некоторые планеты подают сигналы бедствий.
Помогите им!

Чтобы помочь планетам, вам необходимо перейти по ссылке https://forms.yandex.ru/u/6564891843f74f9039916ec9/ .
Жду выполнения задания 29 ноября с 10:00 до 21:00. Отличного полёта!'''
	send_personal_message('img/why.png', mes_text, 1)
	return schedule.CancelJob

def send_personal_message(image, mes_text, role):
	markupReply = types.ReplyKeyboardMarkup(resize_keyboard = True)
	item_1 = types.KeyboardButton('Визитка')
	item_2 = types.KeyboardButton('Дело дня')
	item_3 = types.KeyboardButton('Тематическое задание')
	item_help = types.KeyboardButton('Поддержка')
	markupReply.add(item_1)
	markupReply.add(item_2)
	markupReply.add(item_3)
	markupReply.add(item_help)

	chat_ids = db.get_ids()
	for chat_id in chat_ids:
		if role == db.get_role(chat_id[0]):
			try:
				bot.send_photo(chat_id=chat_id[0], photo=open(image,  'rb'), reply_markup=markupReply,caption=mes_text)
			except:
				pass

def loadText(fileName):
	with open(f'text/{fileName}.txt') as f:
		return f.read()

def main():
	set_scheduled_list()
	threading.Thread(target=scheduled_loop, daemon=True).start()
	with db.conn:
		bot.polling(non_stop="True")

if __name__ == '__main__':
	main()
