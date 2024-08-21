import telebot
from telebot import types
import threading
import time
import subprocess
from pythonping import ping
import datetime


# Создаем словарь для хранения пар логин-пароль
credentials = {
    "User1": "1111",
    "User2": "2222",
   
}

# Укажите токен вашего телеграмм бота
TOKEN = ''
bot = telebot.TeleBot(TOKEN)

authorized = {} # Словарь для хранения авторизации пользователя
last_activity = {}  # Словарь для хранения времени последней активности пользователя
current_user = None  # Глобальное объявление переменной current_user
tracert_results = {}  # Словарь для хранения результатов трассировки по IP-адресам
ast_interaction = {}  # Словарь для хранения времени последнего взаимодействия пользователя с ботом
last_interaction = {}  # Определение переменной last_interactioЫ

def create_keyboard(authorized): # Вывод кнопок при верной авторизации. Если логин\пароль не верны выходит кнопка "Авторизация"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if authorized:
        btn1 = types.KeyboardButton('кнопка 1')
        btn2 = types.KeyboardButton('кнопка 2')
        btn3 = types.KeyboardButton('кнопка 3')
        btn4 = types.KeyboardButton('кнопка 4')
        btn5 = types.KeyboardButton('кнопка 5')
        btn6 = types.KeyboardButton('доп. команды')
        btn7 = types.KeyboardButton('команды')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    else:
        btn_auth = types.KeyboardButton('Авторизация')
        markup.add(btn_auth)
    return markup

def check_activity():
    while True:
        current_time = time.time()
        for user, last_time in last_activity.copy().items():  # Копируем словарь для безопасного итерирования
            if current_time - last_time > 600:  # Проверяем, прошло ли более 10 минут
                authorized.pop(user, None)
                last_activity.pop(user, None)
                try:
                    bot.send_message(user, "Вы были неактивны более 10 минут. Выход из учетной записи.")
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Error sending message to user: {e}")
        time.sleep(60)  # Проверяем активность каждую минуту

# Запуск функции для проверки активности пользователя
activity_thread = threading.Thread(target=check_activity)
activity_thread.start()

# Функция для обработки команды /start независимо от регистра
@bot.message_handler(func=lambda message: message.text.lower() == '/start')
def start(message):
    bot.send_message(message.from_user.id, "Пожалуйста, введите ваш логин:")
    bot.register_next_step_handler(message, check_login)

def check_login(message):
    global current_user
    current_user = message.text
    last_activity[current_user] = time.time()  # Обновляем время последней активности
    bot.send_message(message.from_user.id, "Теперь введите ваш пароль:")
    bot.register_next_step_handler(message, check_password)

def get_greeting():
    current_time = datetime.datetime.now().time()
    if datetime.time(4, 0) <= current_time < datetime.time(11, 0):
        return "Доброе утро!"
    elif datetime.time(11, 0) <= current_time < datetime.time(15, 0):
        return "Добрый день!"
    elif datetime.time(15, 0) <= current_time < datetime.time(22, 0):
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"

def check_password(message):
    password = message.text
    if current_user in credentials and credentials[current_user] == password:
        authorized[current_user] = True
        greeting = get_greeting()
        bot.send_message(message.from_user.id, f"{greeting} {current_user}, авторизация прошла успешна. Можете воспользоваться командами через кнопки, либо написать их в ручную. Для помощи можете нажать кнопки доп. команды, команды или написать команду /help", reply_markup=create_keyboard(True))
    else:
        authorized[current_user] = False
        bot.send_message(message.from_user.id, "Ошибка авторизации. В доступе отказано.", reply_markup=create_keyboard(False))


# Список заранее известных IP-адресов с именами
known_ips = {
    'ip1': [
        {'name': 'ip1', 'ip': '192.168.1.1'},
        {'name': 'ip2', 'ip': '192.168.1.2'},
        {'name': 'ip3', 'ip': '192.168.1.3'},
        
    ],

    'ip2': [
        {'name': 'ip4', 'ip': '192.168.1.4'},
        {'name': 'ip5', 'ip': '192.168.1.5'},
        {'name': 'ip6', 'ip': '192.168.1.6'},
       
    ],

    'ip3': [
        {'name': 'ip7', 'ip': '192.168.1.7'},
        {'name': 'ip8', 'ip': '192.168.1.8'},
        {'name': 'ip9', 'ip': '192.168.1.9'},
        
    ],

    'ip4': [
        {'name': 'ip10', 'ip': '192.168.1.10'},
        {'name': 'ip11', 'ip': '192.168.1.11'},
        {'name': 'ip12', 'ip': '192.168.1.12'},  
    ]
}

# Обработчик команды /get_ping
@bot.message_handler(commands=['get_ping'])
def get_ping_known_ips(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) == 2:  # Проверяем правильность формата команды
            key = command_parts[1].lower()  # Получаем ключ IP-адреса из команды
            if key in known_ips:
                ip_list = known_ips[key]
                for device in ip_list:
                    name = device['name']
                    ip_address = device['ip']
                    ping_result = ping(ip_address, count=4)
                    status = "доступно" if ping_result.success() else "недоступно"
                    response_text = f"Оборудование {name} с IP-адресом {ip_address} {status}"
                    bot.send_message(message.chat.id, response_text)
            else:
                bot.reply_to(message, "Указанный [ключ] не найден.")
        else:
            bot.reply_to(message, "Неверный формат команды. Пожалуйста, используйте /get_ping [ключ].")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при выполнении команды.")


# Список логинов и паролей
known_logs = {
    'Kerio': [
        {'log': 'admin' , 'pas': 'admin'},
    ],

    'Radmin': [
        {'log': 'admin' , 'pas': 'admin'},
    ]
}

# Обработчик команды /secret
@bot.message_handler(commands=['secret'])
def secret_known_logs(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) == 2:  # Проверяем правильность формата команды
            key = command_parts[1]  # Получаем ключ из команды
            found_key = next((k for k in known_logs.keys() if k.lower() == key.lower()), None)
            if found_key:
                user_data = known_logs[found_key]
                for user in user_data:
                    login = user['log']
                    password = user['pas']
                    response_text = f"Login: {login}, Password: {password}"
                    bot.send_message(message.chat.id, response_text)
            else:
                bot.reply_to(message, "Указанный ключ не найден.")
        else:
            bot.reply_to(message, "Неверный формат команды. Пожалуйста, используйте /secret [ключ].")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при выполнении команды.")

# Словарь с ключами и ссылками на ресурсы
resource_links = {
    'Kerio': 'https://yandex.kz/',
    'Nas': 'https://www.kinopoisk.ru/?utm_referrer=yandex.kz'
    # Добавьте другие ключи и ссылки по аналогии
}

# Обработчик команды /link
@bot.message_handler(commands=['link'])
def send_resource_link(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) == 2:  # Проверяем правильность формата команды
            key = command_parts[1]  # Получаем ключ из команды
            found_key = next((k for k in resource_links.keys() if k.lower() == key.lower()), None)
            if found_key:
                link = resource_links[found_key]
                bot.send_message(message.chat.id, link)
            else:
                bot.reply_to(message, "Ссылка для указанного ключа не найдена.")
        else:
            bot.reply_to(message, "Неверный формат команды. Пожалуйста, используйте /link [ключ].")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при выполнении команды.")


@bot.message_handler(commands=['ping'])
def send_ping(message):
    try:
        ip_address = message.text.split()[1]
        ping_result = ping(ip_address, count=4)
        if ping_result.success():
            bot.reply_to(message, f"Оборудование с IP-адресом {ip_address} доступно.")
        else:
            bot.reply_to(message, f"Оборудование с IP-адресом {ip_address} недоступно.")
    except (IndexError, Exception) as e:
        bot.reply_to(message, "Неверный формат команды. Пожалуйста, используйте /ping [IP-адрес].")

@bot.message_handler(commands=['get_tracert'])
def get_tracert(message):
    try:
        ip_address = message.text.split()[1]
        tracert_output = subprocess.check_output(["tracert", ip_address]).decode('cp866')
        bot.reply_to(message, f"Результат трассировки для IP-адреса {ip_address} {tracert_output}")
    except (IndexError, Exception) as e:
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    response_text = """
        Список доступных команд:

        1. /ping [IP-адрес] - Проверить доступность оборудования по IP-адресу.
        2. /get_tracert [IP-адрес] - Получить результат трассировки до указанного IP-адреса.
        3. /get_ping [Ключ] - Проверить доступность оборудования по указаному магазину (ключи (ip1, ip2, ip3, ip4, ip5)).
        4. /secret [Ключ] - Получить логин и пароль (ключи (Kerio, Radmin)).
        5. /link [Ключ] - Получить ссылку на указанный ресурс (ключи (Kerio, Nas)).
    """
    bot.send_message(message.from_user.id, response_text, parse_mode='HTML')


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    last_activity[current_user] = time.time()  # Обновляем время последней активности
    text = message.text.lower()  # Преобразуем текст сообщения к нижнему регистру
    if authorized.get(current_user, False):
        if text == 'привет':
            # Отправка сообщения и кнопок
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('кнопка 1')
            btn2 = types.KeyboardButton('кнопка 2')
            btn3 = types.KeyboardButton('кнопка 3')
            btn4 = types.KeyboardButton('кнопка 4')
            btn5 = types.KeyboardButton('кнопка 5')
            btn6 = types.KeyboardButton('доп. команды')
            btn7 = types.KeyboardButton('команды')
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            bot.send_message(message.from_user.id, 'Привет! Вам нужно выбрать кнопку или ввести нужную команду', reply_markup=create_keyboard(True))
        elif message.text == "доп. команды":
            # Создание списка для ответа
            response_text = """
    *Список дополнительных команд для вывода IP адресов:*
    
        1. ip1_1 [ключ] - Вывод списка ПК ip1_1.

        2. ip2_2 [ключ] - Вывод списка ПК ip2_2.

        3. ip3_3 [ключ] - Вывод списка ПК ip1_1.
    """

            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == "команды":
            # Создание списка для ответа
            response_text = """
            Список доступных команд:

            1. /ping [IP-адрес] - Проверить доступность оборудования по IP-адресу.
            2. /get_tracert [IP-адрес] - Получить результат трассировки до указанного IP-адреса.
            3. /get_ping [Ключ] - Проверить доступность оборудования по указаному магазину (ключи (ip1, ip2, ip3, ip4, ip5)).
            4. /secret [Ключ] - Получить логин и пароль (ключи (Kerio, Radmin)).
            5. /link [Ключ] - Получить ссылку на указанный ресурс (ключи (Kerio, Nas)).
            """
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='HTML')


        elif message.text == "кнопка 1":
            # Создание списка для ответа
            response_text = """
            **Список IP адресов**

            **ПК**

            1.  (K1-PC1) Музыка + видео зал  192.168.1.1
            2.  (K1-PC2) Музыка улица  192.168.1.2
            3.  (K1-PC3) Игровая  192.168.1.3
            
            **Бухгалтерия**

            1.  (K1-PC4) Бухгалтер  192.168.1.4
            2.  (K1-PC5) Бухгалтер по зарабатной плате  192.168.1.5
            3.  (K1-PC6) Бухгалтер  192.168.1.6
            
            **Интернет-магазин**

            1. (K1-PC7) Оператор НСИ  192.168.1.7
            2. (K1-PC8) Маркетолог  192.168.1.8.
            3. (K1-PC9) Старший оператор  192.168.1.9
            """

            # Максимальная длина одной части сообщения
            max_length = 4010

            # Разбиение текста на части
            message_parts = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]

            # Отправка каждой части сообщения
            for part in message_parts:
                bot.send_message(message.from_user.id, part, parse_mode='Markdown')

        # Список адресов Корзина 2
        elif message.text == 'кнопка 2':
        # Создание списка для ответа
            response_text = """
            **Список IP адресов**

            **ПК**

            1.  (K2-PC1)  Оператор 1  192.168.2.1
            2.  (K2-PC2)  Технолог кулинарии  192.168.2.2
            3.  (K2-PC3)  Заместитель директора  192.168.2.3
           
            **Сервера**

            1.  (K2-SR1)  DC (AD, DNS, DHCP) (K2)  192.168.2.4
            2.  (K2-SR2)  Робот (К2)  192.168.2.5
            3.  (K2-SR3)  Обмен 1 (К2)  192.168.2.6
           
            **Кассы**

            1.  Касса 1  192.168.2.7
            2.  Касса 2  192.168.2.8
            3.  Касса 3  192.168.2.9
                       
            **Терминалы**

            1.  (POS #1) Терминал 1 192.168.2.10
            2.  (POS #2) Терминал 2  192.168.2.11
            3.  (POS #3) Терминал 3  192.168.2.12
            """

            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == 'кнопка 3':
            # Создание списка для ответа
            response_text = """
            **Список IP адресов**

            **ПК**

            1.  (К3-PC1)  Технолог пекарни 192.168.3.1
            2.  (К3-PC2)  Бухгалтер кассир 192.168.3.2
            3.  (К3-PC3)  Технолог кулинарии 192.168.3.3
                        
             **Сервера**

            1.  (K3-SR1)  DC (AD, DNS, DHCP)  192.168.3.4
            2.  (K3-SR2)  SQL сервер 192.168.3.5
            3.  (K3-SR3)  Обмен 1 192.168.3.6
           
            **Кассы**

            1.  Касса 1  192.168.3.7
            2.  Касса 2  192.168.3.8
            3.  Касса 3   192.168.3.9
            """

            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == 'кнопка 4':
            # Создание списка для ответа
            response_text = """
            **Список IP адресов**

            **ПК**

            1.  (K4-PC1)  Оператор 1  192.168.4.1
            2.  (K4-PC2)  Оператор 2 192.168.4.2
            3.  (K4-PC3)  Оператор 3 192.168.4.3
                       
            **Сервера**

            1.  (K4-SR1)  Робот  192.168.4.4
            2.  (K4-SR2)  Обмен 1  192.168.4.5
            3.  (K4-SR3)  Обмен 2  192.168.4.6
                        
             **Кассы**

            1.  Касса 1  192.168.4.7
            2.  Касса 2  192.168.4.8
            3.  Касса 3  192.168.4.9
            
            """
           
            # Максимальная длина одной части сообщения
            max_length = 3365

            # Разбиение текста на части
            message_parts = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]

            # Отправка каждой части сообщения
            for part in message_parts:
                bot.send_message(message.from_user.id, part, parse_mode='Markdown')

        elif message.text == 'кнопка 5':

            # Создание списка для ответа
            response_text = """
            **Список IP адресов**

            **ПК**

            1.  (К5-PC1)  Сотрудник IT  192.168.5.1
            2.  (К5-PC2)  Офис-менеджер  192.168.5.2
            3.  (К5-PC3)  Директор сети ТД  192.168.5.3

            """
            
            # Максимальная длина одной части сообщения
            max_length = 3396

            # Разбиение текста на части
            message_parts = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]

            # Отправка каждой части сообщения
            for part in message_parts:
                bot.send_message(message.from_user.id, part, parse_mode='Markdown')

        elif message.text == 'ip1_1':

            # Создание списка для ответа
            response_text = """
            1. (K1-PC1) Музыка + видео зал  192.168.1.1
            2. (K1-PC2) Музыка улица  192.168.1.2
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == 'ip2_2':

            # Создание списка для ответа
            response_text = """
            1. (K2-PC1)  Музыка улица  192.168.2.1
            2. (K2-PC2)  Музыка + видео зал 192.168.2.2
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == 'ip3_3':

            # Создание списка для ответа
            response_text = """
            1. (K3-PC1)  Музыка улица 192.168.3.1
            2. (K3-PC2)  Музыка + видео зал 192.168.3.2
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')


        elif message.text == 'ip4_4':

            # Создание списка для ответа
            response_text = """
            1. (K4-pc1)  Музыка улица  192.168.4.1
            2. (K4-pc2)  Музыка + видео зал 192.168.4.2
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == 'ip5_5':

            # Создание списка для ответа
            response_text = """
            1. (К5-pc1)  Музык   192.168.5.1
            2. (К5-pc2)  Музыка ТД + улица   192.168.5.2
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        elif message.text == 'ip6_6':

            # Создание списка для ответа
            response_text = """
            1. (K1-IG) Игровая  192.168.1.3
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')
        
        elif message.text == 'ip7_7':

            # Создание списка для ответа
            response_text = """
            1. (К5-IG1)  Игровая  192.168.5.3
            2. Планшет (Игровая зона)  192.168.5.4
            """
            
            # Отправка сообщения с ответом в виде списка
            bot.send_message(message.from_user.id, response_text, parse_mode='Markdown')

        else:
            bot.send_message(message.from_user.id, "Извините, я вас не понимаю. Уточните, какую команду хотите выполнить.")
    else:
        if text == "авторизация":
            bot.send_message(message.from_user.id, "Пожалуйста, введите ваш логин для авторизации:")
            bot.register_next_step_handler(message, check_login)
        else:
            bot.send_message(message.from_user.id, "Ошибка авторизации. В доступе отказано.", reply_markup=create_keyboard(False))

        if message.text == "авторизация":
            bot.send_message(message.from_user.id, "Пожалуйста, введите ваш логин для авторизации:")
            bot.register_next_step_handler(message, check_login)

bot.polling(none_stop=True, interval=0)
