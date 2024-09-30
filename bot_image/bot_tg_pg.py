import logging
import re, os
import paramiko
import psycopg2
import shutil
from psycopg2 import Error
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
token = '7279547100:AAFiFI3TBNCt52nsGdqPonwUMzbQV9NOYZw'
host = os.getenv('HOST')
port = os.getenv('PORT')
username = os.getenv('USER')
password = os.getenv('PASSWORD')
pg_host = os.getenv('PG_HOST')
pg_port = os.getenv('PG_PORT')
pg_user = os.getenv('PG_USER')
pg_password = os.getenv('PG_PASSWORD')
pg_db = os.getenv('PG_DB')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Приветствие и список поддерживаемых команд
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!Выбирай команду: \n /find_emails \n /find_phone_number \n /verify_password \n /get_release \n /get_uname \n /get_uptime \n /get_df \n /get_free \n /get_mpstat \n /get_w \n /get_auths \n /get_critical \n /get_ps \n /get_ss \n /get_apt_list \n /get_services \n /get_repl_logs \n /get_emails\n /get_phone_numbers')

# Проверка телефона
def find_phone_command(update: Update, context):
    update.message.reply_text('Введите телефонный номер для поиска: ')
    return 'find_phone_number'

def find_phone_numbers(update: Update, context):
    user_input = update.message.text
    phone_num_regex = re.compile(r'\+?[78]\s?[-\(]?\d{3}\)?\s?-?\d{3}\s?-?\d{2}\s?-?\d{2}')
    phone_list = phone_num_regex.findall(user_input)
    if not phone_list:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    phone_numbers = ''
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with open(f"temp/phone_number.tmp", "w") as file:
        for i in range(len(phone_list)):
            file.write(f'(\'{phone_list[i]}\')\n')
            phone_numbers += f'{i + 1}. {phone_list[i]}\n'
    update.message.reply_text(phone_numbers)
    update.message.reply_text("Сохранить в базу данных? (да/нет)")
    return 'save_phone_number'

def save_phone_number(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'да':
        phone_numbers = ""
        with open(f"temp/phone_number.tmp") as file:
            for line in file:
                phone_numbers += f"{line},"
        insert_phones = phone_numbers.replace("\n", "")[:-1]
        data = pg_command(pg_user, pg_password, pg_host, pg_port, pg_db, f"INSERT INTO Phones(Phone) VALUES{insert_phones};")
        update.message.reply_text(data)
    elif user_input.lower() == 'нет':
        update.message.reply_text("Телефонный номер не сохранен")
    else:
        update.message.reply_text("Не удалось распознать ответ. Телефонный номер не сохранен")
    if os.path.exists('temp'):
        shutil.rmtree('temp')
    return ConversationHandler.END  

# Проверка емаил
def find_emails_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронных адресов: ')
    return 'find_emails'

def find_emails(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Электронные адреса не найдены')
        return ConversationHandler.END
    emails = ''
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with open(f"temp/emails.tmp", "w") as file:
        for i in range(len(emailList)):
            file.write(f'(\'{emailList[i]}\')\n')
            emails += f'{i + 1}. {emailList[i]}\n'
    update.message.reply_text(emails)
    update.message.reply_text("Сохранить в базу данных? да/нет")
    return 'save_email'

def save_email(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'да':
        emails = ""
        with open(f"temp/emails.tmp") as file:
            for line in file:
                emails += f"{line},"
        insert_mails = emails.replace("\n", "")[:-1]
        data = pg_command(pg_user, pg_password, pg_host, pg_port, pg_db, f"INSERT INTO Emails(email) VALUES{insert_mails};")
        update.message.reply_text(data)
    elif user_input.lower() == 'нет':
        update.message.reply_text("Email не сохранен")
    else:
        update.message.reply_text("Не удалось распознать. Email не сохранен")
    if os.path.exists('temp'):
         shutil.rmtree('temp')
    return ConversationHandler.END
# Проверка пароля    
def verify_password_command(update: Update, context):
    update.message.reply_text('Введите ваш пароль:')
    return verify_password

def verify_password(update: Update, context):
    password = update.message.text
    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')
    if password_regex.match(password):
        update.message.reply_text('Пароль сложный.')
    else:
        update.message.reply_text('Пароль простой.')
    return ConversationHandler.END    

# PG
def pg_command(pg_user: str, pg_password: str, pg_host: str, pg_port: str, pg_db: str, command: str) -> any:
    connection = None
    try:
        connection = psycopg2.connect(user=pg_user, password=pg_password, host=pg_host, port=pg_port, database=pg_db)
        cursor = connection.cursor()
        cursor.execute(command)
        if "INSERT" in command:
            connection.commit()
            logging.debug(f"Команда \"{command}\" успешно выполнена")
            return 'Данные добавлены в базу данных'
        else:
            data = cursor.fetchall()
            logging.info(f"Команда \"{command}\" успешно выполнена")
            return data
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        return 'Внутренняя ошибка. Не удалось добавить данные'
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

# Подключение к серверу по ссш
def ssh_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()    
    data = str(data.decode('utf-8')).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    return data
# ИНформация о релизе ОС
def get_release(update: Update, context):
    update.message.reply_text(ssh_command('lsb_release -a'))

# ИНформация о архитектуре
def get_uname(update: Update, context):
    update.message.reply_text(ssh_command('uname -a'))

# Время работы ОС    
def get_uptime(update: Update, context):
    update.message.reply_text(ssh_command('uptime'))

# Информация о файловой системе   
def get_df(update: Update, context):
    update.message.reply_text(ssh_command('df -h'))

# Информация об оперативной памяти    
def get_free(update: Update, context):
    update.message.reply_text(ssh_command('free -h'))

# Производительность системы    
def get_mpstat(update: Update, context):
    update.message.reply_text(ssh_command('mpstat -A'))

# Пользователи    
def get_w(update: Update, context):
    update.message.reply_text(ssh_command('w'))

# Последние 10 входов    
def get_auths(update: Update, context):
    update.message.reply_text(ssh_command('last -n 10'))

# Последние 5 критических событий    
def get_critical(update: Update, context):
    update.message.reply_text(ssh_command('journalctl -p crit -n 5'))

# Запущенные процессы    
def get_ps(update: Update, context):
    update.message.reply_text(ssh_command('ps'))

# Используемые порты    
def get_ss(update: Update, context):
    update.message.reply_text(ssh_command('ss -tulpn'))

# Используемые пакеты
def get_apt_list_command(update: Update, context): 
    update.message.reply_text('Введи название пакета для его поиска или all для вывода всего списка')    
    return 'get_apt_list'
    
def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input == "all":
        update.message.reply_text(ssh_command('dpkg -l|awk \'{print $2}\'|tail -n 100'))
    else:
        update.message.reply_text(ssh_command(f'apt list --installed | grep {user_input}'))
    return ConversationHandler.END    

# Логи репликации
def get_repl_logs(update: Update, context):
    update.message.reply_text(ssh_command('docker logs tm-db_image-1 | grep replication_slot | tail -n 4'))
    
# Запущенные сервисы
def get_services(update: Update, context):
    update.message.reply_text(ssh_command('systemctl list-units --type=service --state=running'))

# Вывод емайлов
def get_emails(update: Update, context):
    connection = None 
    connection = psycopg2.connect(user=pg_user, password=pg_password, host=pg_host, port=pg_port, database=pg_db) 
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM emails") 
    rows = cursor.fetchall() 
    for row in rows: 
        update.message.reply_text(row)
        cursor.close()
        connection.close()

# Вывод телефонов
def get_phone_numbers(update: Update, context):
    connection = None
    connection = psycopg2.connect(user=pg_user, password=pg_password, host=pg_host, port=pg_port, database=pg_db)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM phones") 
    rows = cursor.fetchall() 
    for row in rows: 
        update.message.reply_text(row) 
        cursor.close()
        connection.close()
    
def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(token, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_numbers)],
            'save_phone_number': [MessageHandler(Filters.text & ~Filters.command, save_phone_number)]
        },
        fallbacks=[]
    )
	
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_emails', find_emails_command)],
        states={
            'find_emails': [MessageHandler(Filters.text & ~Filters.command, find_emails)],
            'save_email': [MessageHandler(Filters.text & ~Filters.command, save_email)]
        },
        fallbacks=[]
    )

    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_command)],
        states={
            verify_password: [MessageHandler(Filters.text & ~Filters.command, verify_password)]
        },
        fallbacks=[]
    )
    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)], 
        states={
            'get_apt_list':[MessageHandler(Filters.text & ~Filters.command, get_apt_list)]},
            fallbacks=[]
    )
    
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(conv_handler_verify_password)
    dp.add_handler(convHandlerAptList)
	
    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
