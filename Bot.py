import telebot
from telebot import types
from photo_edit import *

dimensions = dict()
photos = dict()
deltas = dict()
photo_size = dict()

token = ''
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1_cut_photo = types.KeyboardButton("Обрезать фотографию ✂️")
    button2_settings = types.KeyboardButton("Настройки ⚙")
    markup.add(button1_cut_photo, button2_settings)
    dimensions[message.chat.id] = [512, 512]
    bot.send_message(message.chat.id, "Привет, {0.first_name}!\n \n"
                                      "Я умею обрезать Ваши фотографии по нужному размеру.\n \n"
                                      "Если Вы хотите обрезать фотографию, то нажмите на соответствующую кнопку. \n \n"
                                      "По умолчанию стоит формат 512 x 512 пикселей. Если хотите поменять"
                                      " формат, Вам следует изменить его в настройках.".format(message.from_user),
                     reply_markup=markup)


# фунция для вывода кнопок
def InlineKeyboardButtonShift():
    markup_inline = types.InlineKeyboardMarkup(row_width=2)
    button1_agree = types.InlineKeyboardButton(text="Подходит", callback_data='YES')
    button_left = types.InlineKeyboardButton(text="Влево", callback_data='LEFT')
    button_right = types.InlineKeyboardButton(text="Вправо", callback_data='RIGHT')
    button_down = types.InlineKeyboardButton(text="Вниз", callback_data='DOWN')
    button_up = types.InlineKeyboardButton(text="Вверх", callback_data='UP')
    markup_inline.add(button_left, button_right, button_down, button_up, button1_agree)
    return markup_inline


# как-то в параметре передается состояние фотки: конечное(чтобы уже вывести) или промежуточное
def receive_photo_handler(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        photos[message.chat.id] = downloaded_file
        image = Image.open(io.BytesIO(downloaded_file))
        width, height = image.size
        photo_size[message.chat.id] = [0, 0]
        photo_size[message.chat.id][0] = width
        photo_size[message.chat.id][1] = height
        cut_photo(message)
    except TypeError:
            if message.text == "Настройки ⚙":
                menu_message(message)
            else:
                bot.send_message(message.chat.id, text="Пришлите, пожалуйста, фотографию!")
                bot.register_next_step_handler(message, receive_photo_handler)


def cut_photo(message):
    deltas[message.chat.id] = [0, 0]
    bot.send_photo(message.chat.id,
                   edit_photo(photos[message.chat.id], dimensions[message.chat.id][0], dimensions[message.chat.id][1]))


    markup_inline = InlineKeyboardButtonShift()
    bot.send_message(message.chat.id,
                     "Ваша будущая фотография находится в красной рамке.")
    bot.send_message(message.chat.id, "Подходит ли Вам такое расположение?", reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True, )
def answer(call):
    if call.data == 'YES':
        bot.send_message(call.message.chat.id, 'Пожалуйста, получите Вашу фотографию в виде файла.')
        bot.send_document(call.message.chat.id,
                          document=crop_picture(photos[call.message.chat.id], dimensions[call.message.chat.id][0],
                                                dimensions[call.message.chat.id][1], deltas[call.message.chat.id][0],
                                                deltas[call.message.chat.id][1]))
        deltas[call.message.chat.id][0] = 0
        deltas[call.message.chat.id][1] = 0
        photos[call.message.chat.id] = 0
        photo_size[call.message.chat.id][0] = 0
        photo_size[call.message.chat.id][1] = 0
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bot.register_next_step_handler(call.message, receive_photo_handler)


    elif call.data == 'LEFT':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        deltas[call.message.chat.id][0] -= max(
            (photo_size[call.message.chat.id][0] // 2) - dimensions[call.message.chat.id][0] // 2 +
            deltas[call.message.chat.id][0], 0) // 6

        bot.send_photo(call.message.chat.id,
                       edit_photo(photos[call.message.chat.id], dimensions[call.message.chat.id][0],
                                  dimensions[call.message.chat.id][1], deltas[call.message.chat.id][0],
                                  deltas[call.message.chat.id][1]))
        markup_inline = InlineKeyboardButtonShift()
        bot.send_message(call.message.chat.id, "Подходит ли Вам такое расположение?", reply_markup=markup_inline)

    elif call.data == 'RIGHT':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        deltas[call.message.chat.id][0] += max(
            (photo_size[call.message.chat.id][0] // 2) - dimensions[call.message.chat.id][0] // 2 -
            deltas[call.message.chat.id][0], 0) // 6

        bot.send_photo(call.message.chat.id,
                       edit_photo(photos[call.message.chat.id], dimensions[call.message.chat.id][0],
                                  dimensions[call.message.chat.id][1], deltas[call.message.chat.id][0],
                                  deltas[call.message.chat.id][1]))
        markup_inline = InlineKeyboardButtonShift()
        bot.send_message(call.message.chat.id, "Подходит ли Вам такое расположение?", reply_markup=markup_inline)

    elif call.data == 'UP':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        deltas[call.message.chat.id][1] -= max(
            (photo_size[call.message.chat.id][1] // 2) - dimensions[call.message.chat.id][1] // 2 +
            deltas[call.message.chat.id][1], 0) // 6

        bot.send_photo(call.message.chat.id,
                       edit_photo(photos[call.message.chat.id], dimensions[call.message.chat.id][0],
                                  dimensions[call.message.chat.id][1], deltas[call.message.chat.id][0],
                                  deltas[call.message.chat.id][1]))
        markup_inline = InlineKeyboardButtonShift()
        bot.send_message(call.message.chat.id, "Подходит ли Вам такое расположение?", reply_markup=markup_inline)

    elif call.data == 'DOWN':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        deltas[call.message.chat.id][1] += max(
            (photo_size[call.message.chat.id][1] // 2) - dimensions[call.message.chat.id][1] // 2 -
            deltas[call.message.chat.id][1], 0) // 6

        bot.send_photo(call.message.chat.id,
                       edit_photo(photos[call.message.chat.id], dimensions[call.message.chat.id][0],
                                  dimensions[call.message.chat.id][1], deltas[call.message.chat.id][0],
                                  deltas[call.message.chat.id][1]))
        markup_inline = InlineKeyboardButtonShift()
        bot.send_message(call.message.chat.id, "Подходит ли Вам такое расположение?", reply_markup=markup_inline)


@bot.message_handler(content_types=['text'])
def menu_message(message):

    if message.text == "Обрезать фотографию ✂️":
        bot.send_message(message.chat.id, text="Пришлите, пожалуйста, фото, которое хотите обрезать.")
        bot.register_next_step_handler(message, receive_photo_handler)


    elif message.text == "Настройки ⚙":
        bot.send_message(message.chat.id, text="По умолчанию стоит формат 512 x 512 пикселей.\n \n"
                                               "Если хотите поменять размер будущей фотографии, то напишите размер "
                                               "в формате: длина ширина.\n"
                                               "(обязательно через пробел)\n \n"
                                               "Пример: 412 420")

        bot.register_next_step_handler(message, message_grab_new_size)

    else:
        bot.send_message(message.chat.id, text="Нажмите, пожалуйста, на кнопку.")


# функция запоминает координаты пользователя
def message_grab_new_size(message):
    try:
        width, height = message.text.split()
        dimensions_x = int(width)
        dimensions_y = int(height)
        if dimensions_y < 20 or dimensions_x < 20:
            raise TypeError
        dimensions[message.chat.id] = [dimensions_x, dimensions_y]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1_cut_photo = types.KeyboardButton("Обрезать фотографию ✂️")
        button2_settings = types.KeyboardButton("Настройки ⚙")
        markup.add(button1_cut_photo, button2_settings)
        bot.send_message(message.chat.id, f'Вы выбрали размер: {dimensions_x} {dimensions_y}', reply_markup=markup)


    except (AttributeError, ValueError) as e:
        if message.text == "Обрезать фотографию ✂️":
            menu_message(message)
        else:
            bot.send_message(message.chat.id, text="Введите, пожалуйста, числа по формату.")
            bot.register_next_step_handler(message, message_grab_new_size)
    except TypeError:
        bot.send_message(message.chat.id, text="Введите, пожалуйста, числа побольше.")
        bot.register_next_step_handler(message, message_grab_new_size)


while(True):
    try:
        bot.infinity_polling()
    except:
        pass