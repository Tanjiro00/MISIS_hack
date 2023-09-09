import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
import database
from transformers import AutoTokenizer, AutoModel
import torch


bot = telebot.TeleBot('6352909336:AAGIzccUfiU-p9LGLA6R1aKtz4pecz1tjRc')
tokenizer = AutoTokenizer.from_pretrained('uaritm/multilingual_en_uk_pl_ru')
model = AutoModel.from_pretrained('uaritm/multilingual_en_uk_pl_ru')


@bot.message_handler(commands=['start'])
def start(msg):
    text = f"Привет, {msg.from_user.first_name}! \n\nЭто сервис, который помогает найти ученикам университета новые знакомства. " + \
            "Для начала работы стоит заполнить небольшую анкету."
    bot.send_message(msg.chat.id, text)
    sent = bot.send_message(msg.chat.id, 'Как тебя зовут?')
    profile_data = {'user_id': msg.chat.id}
    bot.register_next_step_handler(sent, get_name, profile_data)


def get_name(msg, profile_data):
    profile_data['name'] = msg.text
    text = "С какого ты института?"

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("ИКН")
    item2 = telebot.types.KeyboardButton("ИБО")
    item3 = telebot.types.KeyboardButton("ИНМиН")
    item4 = telebot.types.KeyboardButton("ЭкоТех")
    item5 = telebot.types.KeyboardButton("МГИ")
    item6 = telebot.types.KeyboardButton("ЭУПП")

    markup.add(item1, item2, item3, item4, item5, item6)

    sent = bot.send_message(msg.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, get_institut, profile_data)


def get_institut(msg, profile_data):
    profile_data['institut'] = msg.text
    text = "Супер! На каком направлении ты учишься?"
    sent = bot.send_message(msg.chat.id, text, reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent, get_program, profile_data)


def get_program(msg, profile_data):
    profile_data['program'] = msg.text
    text = "Классно) На каком ты курсе?"
    sent = bot.send_message(msg.chat.id, text)
    bot.register_next_step_handler(sent, get_course, profile_data)


def get_course(msg, profile_data):
    profile_data['course'] = msg.text
    text = "Отлично! Теперь тебе нужно выбрать студенческие объединения, в которых ты состоишь.\n" + \
           "Снизу появятся кнопочки, с выбором объединений, их можно выбрать несколько. Если ты ни в чем не состоишь, " + \
            "или ты закончил выбирать объединения, нажми кнопку СТОП"

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    unions = [
        'СТОП',
        'Студенческий совет',
        'Студенческое научное общество',
        'MISIS Media',
        'Клуб интернациональной дружбы',
        'International Student Council of NUST MISIS',
        'Турклуб НИТУ МИСИС',
        'Волонтерский клуб',
        'Студенческий совет общежитий',
        'Творческая лаборатория «Арт Лаб»',
        'MISIS eSports',
        'Академия амбассадоров НИТУ МИСИС',
        'Клуб студенческих наставников',
        'Студенческое конструкторское бюро ИТО',
        'Экологический клуб «Green MISIS»',
        'Объединение спортивных клубов МИСИС',
        'Хакатон-клуб ITAM',
        'Дизайн-клуб ITAM',
        'Геймдев-клуб МИСИС ITAM',
        'Центр карьерного продвижения',
        'Клуб проектных инициатив',
        'Инкубатор технологических проектов',
        'Патриотический клуб'
    ]
    for union in unions:
        markup.add(telebot.types.KeyboardButton(union))
    profile_unions = []
    sent = bot.send_message(msg.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, get_unions, profile_data, profile_unions, markup)


def get_unions(msg, profile_data, profile_unions, markup):
    if str(msg.text).upper() == 'СТОП':
        profile_data['unions'] = profile_unions
        text = 'Спасибо) Теперь тебе нужно выбрать несколько категорий, в которых ты специализируешься.\n' + \
               'Выбери несколько, как только выберешь, нажми кнопку СТОП'
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        subjects = [
            'СТОП',
            'Математика',
            'Информатика',
            'Литература',
            'Иностранные языки',
            'История',
            'География',
            'Биология',
            'Химия',
            'Физика',
            'Дизайн',
            'Обществознание'
        ]
        profile_subjects = []
        for subject in subjects:
            markup.add(telebot.types.KeyboardButton(subject))
        sent = bot.send_message(msg.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(sent, get_subjects, profile_data, profile_subjects, markup)

    else:
        profile_unions.append(msg.text)
        texts = ['Записал)', 'Отметил)', 'Увидел', 'Зафиксировал', 'Внес']
        sent = bot.send_message(msg.chat.id, random.choice(texts), reply_markup=markup)
        bot.register_next_step_handler(sent, get_unions, profile_data, profile_unions, markup)


def get_subjects(msg, profile_data, profile_subjects, markup):
    if str(msg.text).upper() == 'СТОП':
        profile_data['subjects'] = profile_subjects
        text = 'Спасибо) Теперь напиши небольшую текстовую анкету...(дописать)'
        sent = bot.send_message(msg.chat.id, text, reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(sent, get_text, profile_data)
    else:
        profile_subjects.append(msg.text)
        texts = ['Записал)', 'Отметил)', 'Увидел', 'Зафиксировал', 'Внес']
        sent = bot.send_message(msg.chat.id, random.choice(texts), reply_markup=markup)
        bot.register_next_step_handler(sent, get_subjects, profile_data, profile_subjects, markup)


def get_text(msg, profile_data):
    profile_data['text'] = msg.text
    text = 'Отлично! Теперь проверь свою анкету. Если хочешь перезаполнить - напиши /start'
    bot.send_message(msg.chat.id, text)
    text = f"Имя: {profile_data['name']}\n" + \
           f"Институт: {profile_data['institut']}\n" + \
           f"Направление обучения: {profile_data['program']}\n" + \
           f"Курс: {profile_data['course']}\n" + \
           f"Объединения: {', '.join(profile_data['unions'])}\n" + \
           f"Интересы: {', '.join(profile_data['subjects'])}\n" + \
           f"{profile_data['text']}"
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = telebot.types.KeyboardButton("Все хорошо")
    markup.add(item2)
    sent = bot.send_message(msg.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, is_done, profile_data)


def emb_creation(man_ancket, model, tokenizer):
    '''
    Create embedding for persons(if function get one ancket return vector else tensor with shape [num_ancket, 768])
    '''
    tokenized_text = tokenizer(text=man_ancket, return_tensors='pt', padding=True)
    with torch.no_grad():
        model_output = model(**tokenized_text)
    sentence_embeddings = _mean_pooling(model_output, tokenized_text['attention_mask']).squeeze()
    #all_embeddings = torch.cat((all_embeddings, sentence_embeddings), 0)
    return sentence_embeddings


#Mean Pooling - Take attention mask into account for correct averaging


def _mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    print(token_embeddings.shape, 'emb', attention_mask.shape, 'att')
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    print(input_mask_expanded.shape)
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def is_done(msg, profile_data):
    if msg.text == 'Все хорошо':
        text = 'Отлично)'
        sent = bot.send_message(msg.chat.id, text)

        emb = emb_creation(profile_data['text'], model, tokenizer)
        emb = emb.detach().cpu().tolist()
        profile_data['embs'] = emb

        database.insert_varible_into_table(profile_data)
        print(database.get_developer_info(str(msg.chat.id)))
        bot.register_next_step_handler(sent, select_mode)
    elif msg.text == 'Заново заполнить':
        bot.register_next_step_handler(msg, start)
    else:
        text = 'Я понимаю только текст из кнопок)'
        bot.send_message(msg.chat.id, text)
        bot.register_next_step_handler(msg, get_text, profile_data)


def select_mode(msg):
    pass


bot.infinity_polling()