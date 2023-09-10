import pandas as pd
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
import database
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

with open('api_key.txt', 'r') as f:
    API_TOKEN = f.readline()
bot = telebot.TeleBot(API_TOKEN)
tokenizer = AutoTokenizer.from_pretrained('uaritm/multilingual_en_uk_pl_ru')
model = AutoModel.from_pretrained('uaritm/multilingual_en_uk_pl_ru')


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

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.from_user.username:
        text = f"Привет, {msg.from_user.first_name}! \n\nЭто сервис, который помогает найти ученикам университета новые знакомства. " + \
               "Для начала работы стоит заполнить небольшую анкету."
        bot.send_message(msg.chat.id, text)
        database.delete_user(msg.chat.id)
        sent = bot.send_message(msg.chat.id, 'Как тебя зовут?')
        profile_data = {'user_id': msg.chat.id, 'username': msg.from_user.username}
        bot.register_next_step_handler(sent, get_name, profile_data)
    else:
        text = "Чтобы начать работу, вам нужно в настройках своего профиля указать имя пользователя (username). \n" + \
                "Это нужно для того, чтобы мы могли дать ваши контакты при знакомстве."
        bot.send_message(msg.from_user.id, text)


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

    for union in unions:
        markup.add(telebot.types.KeyboardButton(union))
    profile_unions = []
    sent = bot.send_message(msg.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, get_unions, profile_data, profile_unions, markup)

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

def get_unions(msg, profile_data, profile_unions, markup):
    if str(msg.text).upper() == 'СТОП':
        profile_data['unions'] = list(set(profile_unions))
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
        profile_data['subjects'] = list(set(profile_subjects))
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
           f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
           f"{profile_data['text']}"
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = telebot.types.KeyboardButton("Все хорошо")
    markup.add(item2)
    sent = bot.send_message(msg.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, is_done, profile_data)


class Emb_Creator:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('uaritm/multilingual_en_uk_pl_ru')
        self.model = AutoModel.from_pretrained('uaritm/multilingual_en_uk_pl_ru')
        self.cos = torch.nn.CosineSimilarity(dim=1)
        self.all_embeddings = torch.tensor([])
        self.subjects = [
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

    # Mean Pooling - Take attention mask into account for correct averaging
    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def emb_creation(self, man_ancket):
        '''
        Create embedding for persons(if function get one ancket return vector else tensor with shape [num_ancket, 768])
        '''
        tokenized_text = self.tokenizer(text=man_ancket, return_tensors='pt', padding=True)
        with torch.no_grad():
            model_output = self.model(**tokenized_text)
        sentence_embeddings = self._mean_pooling(model_output, tokenized_text['attention_mask']).squeeze()
        if len(sentence_embeddings.shape) == 1:
            self.all_embeddings = torch.cat((self.all_embeddings, sentence_embeddings), 0)
        else:
            self.all_embeddings = torch.cat((self.all_embeddings, sentence_embeddings), 0)
        return sentence_embeddings

    def get_cos_sim(self, df, idx, k=1, return_max=True):
        '''
        func get index of person and return cos_sim of person with every man from BD
        '''
        man = df[df.user_id == idx]['embs']
        other_man = df[df.user_id != idx]
        encode_user_subjects = self.encode_subs(df[df.user_id == idx]['subjects'].values[0])
        encode_all_users_subjects = list(map(self.encode_subs, other_man['subjects'].values))
        cos_sim_subjects = torch.tensor(cosine_similarity([encode_user_subjects], encode_all_users_subjects))

        other_man = df[df.user_id != idx]
        other_embeddings = other_man['embs']
        # other_embeddings = torch.index_select(self.all_embeddings, 0, indices)
        tensor1 = list(map(lambda x: torch.tensor(x), man.values))
        tensor2 = list(map(lambda x: torch.tensor(x), other_embeddings.values))
        cosine_arr = (self.cos(tensor1[0], torch.stack(tensor2, dim=0)) + cos_sim_subjects)/2
        print(self.cos(tensor1[0], torch.stack(tensor2, dim=0)))
        print(cos_sim_subjects)
        print(cosine_arr)
        if return_max:
            # print(cosine_arr, 'cosine')
            max_sim_idx = torch.topk(cosine_arr, k).indices
            # print(max_sim_idx)
            # max_sim_person = other_man.user_id[other_man.iloc[max_sim_idx == other_man.user_id]
            return other_man.iloc[int(max_sim_idx[0][0])].user_id
        min_sim_idx = torch.topk(1 / (cosine_arr * 100),
                                 k).indices  # I need get min topk but I lazy and I solve invert numbers(I dont want to search min topk method)
        min_sim_person = other_man.iloc[int(min_sim_idx[0][0])].user_id
        return min_sim_person

    def encode_subs(self, lst_of_subs):
        encoded_subjects = [0 for i in range(11)]
        for i in lst_of_subs:
            if i in self.subjects:
                encoded_subjects[self.subjects.index(i)] = 1
            # indices = torch.tensor([el for el in df.indexes if el != idx])
        return encoded_subjects


model = Emb_Creator()


def is_done(msg, profile_data):
    if msg.text == 'Все хорошо':
        text = 'Отлично)'
        sent = bot.send_message(msg.chat.id, text, reply_markup=ReplyKeyboardRemove())

        emb = model.emb_creation(profile_data['text'])
        emb = emb.detach().cpu().tolist()
        profile_data['embs'] = emb

        database.insert_varible_into_table(profile_data)
        print(database.get_developer_info(str(msg.chat.id)))
        menu(msg)
    elif msg.text == 'Заново заполнить':
        bot.register_next_step_handler(msg, start)
    else:
        text = 'Я понимаю только текст из кнопок)'
        bot.send_message(msg.chat.id, text)
        bot.register_next_step_handler(msg, is_done, profile_data)


def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    # markup.add(InlineKeyboardButton("Наиболее близкий собеседник", callback_data="mode_1"))
    # markup.add(InlineKeyboardButton("Наиболее не похожий собеседник", callback_data="mode_2"))
    # markup.add(InlineKeyboardButton("Cлучайный пользователь", callback_data="mode_3"))
    # markup.add(InlineKeyboardButton("Поиск по категориям", callback_data="mode_4"))
    markup.add(InlineKeyboardButton("Найти собеседника", callback_data="set_mode"))
    markup.add(InlineKeyboardButton("Помощь", callback_data="help"),
               InlineKeyboardButton("Заполнить анкету заново", callback_data="restart"))
    markup.add(InlineKeyboardButton("Полученные анкеты", callback_data="offers"))
    return markup


def set_mode(call):
    text = "Выбери один из режимов поиска собеседника:"
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    markup.add(InlineKeyboardButton("Наиболее близкий собеседник", callback_data="mode_1"))
    markup.add(InlineKeyboardButton("Наиболее не похожий собеседник", callback_data="mode_2"))
    markup.add(InlineKeyboardButton("Cлучайный пользователь", callback_data="mode_3"))
    markup.add(InlineKeyboardButton("Поиск по категориям", callback_data="mode_4"))
    bot.send_message(call.from_user.id, text, reply_markup=markup)


@bot.message_handler(commands=['menu'])
def menu(msg):
    text = f"{msg.from_user.first_name}, что ты хочешь сделать?"
    bot.send_message(msg.from_user.id, text, reply_markup=menu_markup())


@bot.message_handler(commands=['mode_1'])
def mode_1(call):
    data_user = database.get_developer_info(str(call.from_user.id))
    df_embs = database.create_df_embs(str(call.from_user.id))
    if not(df_embs[df_embs.user_id != str(call.from_user.id)].empty):
        rec_user = model.get_cos_sim(df_embs, str(call.from_user.id))
        data_other = database.get_developer_info(str(rec_user))
        text = f"Рекомендованный собеседник: \n\n" + \
               f"Имя: {data_other['name']}\n" + \
               f"Институт: {data_other['institut']}\n" + \
               f"Направление обучения: {data_other['program']}\n" + \
               f"Курс: {data_other['course']}\n" + \
               f"Объединения: {', '.join(data_other['unions'])}\n" + \
               f"Интересы: {', '.join(data_other['subjects'])}\n\n" + \
               f"{data_other['text']}"

        def choice_markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Хочу познакомиться", callback_data=f"accept_mode1|{str(rec_user)}"),
                       InlineKeyboardButton("Подобрать следующего", callback_data=f"skip_mode1|{str(rec_user)}"))
            return markup

        bot.send_message(call.from_user.id, text, reply_markup=choice_markup())
    else:
        bot.send_message(call.from_user.id, 'Закончились анкеты(')


@bot.message_handler(commands=['mode_2'])
def mode_2(call):
    data_user = database.get_developer_info(str(call.from_user.id))
    df_embs = database.create_df_embs(str(call.from_user.id))
    if not (df_embs[df_embs.user_id != str(call.from_user.id)].empty):
        rec_user = model.get_cos_sim(df_embs, str(call.from_user.id), return_max=False)
        data_other = database.get_developer_info(str(rec_user))
        text = f"Рекомендованный собеседник: \n\n" + \
               f"Имя: {data_other['name']}\n" + \
               f"Институт: {data_other['institut']}\n" + \
               f"Направление обучения: {data_other['program']}\n" + \
               f"Курс: {data_other['course']}\n" + \
               f"Объединения: {', '.join(data_other['unions'])}\n" + \
               f"Интересы: {', '.join(data_other['subjects'])}\n\n" + \
               f"{data_other['text']}"

        def choice_markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Хочу познакомиться", callback_data=f"accept_mode1|{str(rec_user)}"),
                       InlineKeyboardButton("Подобрать следующего", callback_data=f"skip_mode1|{str(rec_user)}"))
            return markup

        bot.send_message(call.from_user.id, text, reply_markup=choice_markup())
    else:
        bot.send_message(call.from_user.id, 'Закончились анкеты(')


@bot.message_handler(commands=['mode_3'])
def mode_3(call):
    df = database.get_users_without_users_id(str(call.from_user.id))
    if not(df.empty):
        profile_data = df.iloc[0]
        text = f"Имя: {profile_data['name']}\n" + \
               f"Институт: {profile_data['institut']}\n" + \
               f"Направление обучения: {profile_data['program']}\n" + \
               f"Курс: {profile_data['num_course']}\n" + \
               f"Объединения: {', '.join(profile_data['unions'])}\n" + \
               f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
               f"{profile_data['anketa']}"
        def choice_markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Хочу познакомиться", callback_data=f"accept_mode1|{str(profile_data['user_id'])}"),
                       InlineKeyboardButton("Подобрать следующего", callback_data=f"skip_mode1|{str(profile_data['user_id'])}"))
            return markup
        bot.send_message(call.from_user.id, text, reply_markup=choice_markup())
    else:
        bot.send_message(call.from_user.id, 'Анкеты закончились(')


@bot.message_handler(commands=['mode_4'])
def mode_4(call):
    text = "Выбери, в какой категории найти тебе собеседника. Здесь можно найти себе человека, который разбирается в той" + \
           " или иной сфере"
    def markup():
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Институт", callback_data=f"mode_institut"),
                   InlineKeyboardButton("Предмет", callback_data=f"mode_subject"))
        markup.add(InlineKeyboardButton('Студ. объединение', callback_data=f"mode_union"))
        return markup
    bot.send_message(call.from_user.id, text, reply_markup=markup())


def mode_institut(call):
    text = "Выбери институт, из которого ты хочешь найти человека:"
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = telebot.types.KeyboardButton("ИКН")
    item2 = telebot.types.KeyboardButton("ИБО")
    item3 = telebot.types.KeyboardButton("ИНМиН")
    item4 = telebot.types.KeyboardButton("ЭкоТех")
    item5 = telebot.types.KeyboardButton("МГИ")
    item6 = telebot.types.KeyboardButton("ЭУПП")

    markup.add(item1, item2, item3, item4, item5, item6)
    sent = bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, find_institut, 'msg')


def find_institut(msg, institut):
    if institut == 'msg': institut = msg.text
    df = database.get_user_institut(institut, msg.from_user.id)
    if not(df.empty):
        profile_data = df.iloc[0]
        text = f"Имя: {profile_data['name']}\n" + \
               f"Институт: {profile_data['institut']}\n" + \
               f"Направление обучения: {profile_data['program']}\n" + \
               f"Курс: {profile_data['num_course']}\n" + \
               f"Объединения: {', '.join(profile_data['unions'])}\n" + \
               f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
               f"{profile_data['anketa']}"
        def choice_markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Хочу познакомиться", callback_data=f"accept_mode_i|{str(profile_data['user_id'])}|{institut}"),
                       InlineKeyboardButton("Подобрать следующего", callback_data=f"skip_mode_i|{str(profile_data['user_id'])}|{institut}"))
            return markup
        bot.send_message(msg.from_user.id, text, reply_markup=choice_markup())
    else:
        bot.send_message(msg.from_user.id, 'Анкеты закончились(')


def mode_subject(call):
    text = "Выбери предмет, мы подберем собеседника, который разбирается в этом предмете:"

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in subjects:
        if subject != 'СТОП':
            markup.add(telebot.types.KeyboardButton(subject))
    sent = bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, find_subject, 'msg')


def find_subject(msg, subject):
    if subject == 'msg': subject = msg.text
    df = database.get_user_some('subjects', subject, msg.from_user.id)
    if not (df.empty):
        profile_data = df.iloc[0]
        text = f"Имя: {profile_data['name']}\n" + \
               f"Институт: {profile_data['institut']}\n" + \
               f"Направление обучения: {profile_data['program']}\n" + \
               f"Курс: {profile_data['num_course']}\n" + \
               f"Объединения: {', '.join(profile_data['unions'])}\n" + \
               f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
               f"{profile_data['anketa']}"

        def choice_markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Хочу познакомиться",
                                            callback_data=f"accept_mode_s|{str(profile_data['user_id'])}|{subject}"),
                       InlineKeyboardButton("Подобрать следующего",
                                            callback_data=f"skip_mode_s|{str(profile_data['user_id'])}|{subject}"))
            return markup

        bot.send_message(msg.from_user.id, text, reply_markup=choice_markup())
    else:
        bot.send_message(msg.from_user.id, 'Анкеты закончились(')


def mode_union(call):
    text = "Выбери студ. объединение, в котором вы хотите найти человека:"

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in unions:
        if subject != 'СТОП':
            markup.add(telebot.types.KeyboardButton(subject))
    sent = bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, find_unions, 'msg')


def find_unions(msg, union):
    if union == 'msg': union = msg.text
    df = database.get_user_some('unions', union, msg.from_user.id)
    if not (df.empty):
        profile_data = df.iloc[0]
        text = f"Имя: {profile_data['name']}\n" + \
               f"Институт: {profile_data['institut']}\n" + \
               f"Направление обучения: {profile_data['program']}\n" + \
               f"Курс: {profile_data['num_course']}\n" + \
               f"Объединения: {', '.join(profile_data['unions'])}\n" + \
               f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
               f"{profile_data['anketa']}"

        def choice_markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Хочу познакомиться",
                                            callback_data=f"accept_mode_u|{str(profile_data['user_id'])}|{union}"),
                       InlineKeyboardButton("Подобрать следующего",
                                            callback_data=f"skip_mode_u|{str(profile_data['user_id'])}|{union}"))
            return markup

        bot.send_message(msg.from_user.id, text, reply_markup=choice_markup())
    else:
        bot.send_message(msg.from_user.id, 'Анкеты закончились(')



@bot.message_handler(commands=['offers'])
def offers(msg):
    offers_id = database.get_offers(str(msg.from_user.id))
    bot.send_message(msg.from_user.id, f"Количество анкет: {len(offers_id)}")
    if len(offers_id) > 0:
        user_id = offers_id[0]
        profile_data = database.get_developer_info(user_id)
        text = f"Имя: {profile_data['name']}\n" + \
               f"Институт: {profile_data['institut']}\n" + \
               f"Направление обучения: {profile_data['program']}\n" + \
               f"Курс: {profile_data['course']}\n" + \
               f"Объединения: {', '.join(profile_data['unions'])}\n" + \
               f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
               f"{profile_data['text']}"

        def markup():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Принять", callback_data=f"like|{str(user_id)}"),
                       InlineKeyboardButton("Отказать", callback_data=f"dislike|{str(user_id)}"))
            markup.add(InlineKeyboardButton('Пропустить', callback_data=f"offer_skip|{str(user_id)}"))
            return markup

        bot.send_message(msg.from_user.id, text, reply_markup=markup())


@bot.message_handler(commands=['help'])
def help_user(msg):
    text = "Текст, который стоит дописать для помощи"
    bot.send_message(msg.from_user.id, text)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "mode_1":
        mode_1(call)

    if call.data == "mode_2":
        mode_2(call)

    if call.data == "mode_3":
        mode_3(call)

    if call.data == "mode_4":
        mode_4(call)

    if call.data == 'mode_institut':
        mode_institut(call)

    if call.data == 'mode_subject':
        mode_subject(call)

    if call.data == 'mode_union':
        mode_union(call)

    if call.data == "set_mode":
        set_mode(call)

    if call.data[:12] == 'accept_mode1':
        rec_user = call.data[13:]
        text = "Мы отправили этому пользователю вашу анкету, если он захочет с вами познакомиться, мы вышлем вам его контакты."
        bot.send_message(call.from_user.id, text)
        database.insert_into_actions(str(call.from_user.id), rec_user, 'send_offer')
        text = 'Одному из пользователей понравилась ваша анкета и он хочет с вами познакомиться!' + \
                '\nНапишите /offers для просмотра анкет)'
        bot.send_message(int(rec_user), text)
        menu(call)

    if call.data[:10] == 'skip_mode1':
        rec_user = call.data[11:]
        database.insert_into_actions(str(call.from_user.id), rec_user, 'skip')
        mode_1(call)

    if call.data[:13] == 'accept_mode_i':
        rec_user = str(call.data).split('|')[1]
        text = "Мы отправили этому пользователю вашу анкету, если он захочет с вами познакомиться, мы вышлем вам его контакты."
        bot.send_message(call.from_user.id, text)
        database.insert_into_actions(str(call.from_user.id), rec_user, 'send_offer')
        text = 'Одному из пользователей понравилась ваша анкета и он хочет с вами познакомиться!' + \
                '\nНапишите /offers для просмотра анкет)'
        bot.send_message(int(rec_user), text)
        menu(call)

    if call.data[:11] == 'skip_mode_i':
        rec_user, institut = str(call.data).split('|')[1], str(call.data).split('|')[2]
        database.insert_into_actions(str(call.from_user.id), rec_user, 'skip')
        find_institut(call, institut)

    if call.data[:13] == 'accept_mode_s':
        rec_user = str(call.data).split('|')[1]
        text = "Мы отправили этому пользователю вашу анкету, если он захочет с вами познакомиться, мы вышлем вам его контакты."
        bot.send_message(call.from_user.id, text)
        database.insert_into_actions(str(call.from_user.id), rec_user, 'send_offer')
        text = 'Одному из пользователей понравилась ваша анкета и он хочет с вами познакомиться!' + \
                '\nНапишите /offers для просмотра анкет)'
        bot.send_message(int(rec_user), text)
        menu(call)

    if call.data[:11] == 'skip_mode_s':
        rec_user, subject = str(call.data).split('|')[1], str(call.data).split('|')[2]
        database.insert_into_actions(str(call.from_user.id), rec_user, 'skip')
        find_subject(call, subject)

    if call.data[:13] == 'accept_mode_u':
        rec_user = str(call.data).split('|')[1]
        text = "Мы отправили этому пользователю вашу анкету, если он захочет с вами познакомиться, мы вышлем вам его контакты."
        bot.send_message(call.from_user.id, text)
        database.insert_into_actions(str(call.from_user.id), rec_user, 'send_offer')
        text = 'Одному из пользователей понравилась ваша анкета и он хочет с вами познакомиться!' + \
                '\nНапишите /offers для просмотра анкет)'
        bot.send_message(int(rec_user), text)
        menu(call)

    if call.data[:11] == 'skip_mode_u':
        rec_user, union = str(call.data).split('|')[1], str(call.data).split('|')[2]
        database.insert_into_actions(str(call.from_user.id), rec_user, 'skip')
        find_unions(call, union)

    if call.data[:4] == 'like':
        rec_user = call.data[5:]
        profile_user2 = database.get_developer_info(rec_user)
        text = f"Отлично! Вот контакты этого пользователя: @{profile_user2['username']}\nРад был помочь познакомиться)"
        bot.send_message(call.from_user.id, text)
        profile_data = database.get_developer_info(str(call.from_user.id))
        text = f"Пользователь @{call.from_user.username} дал согласие на знакомство) Напомню его анкету:\n"+ \
               f"Имя: {profile_data['name']}\n" + \
               f"Институт: {profile_data['institut']}\n" + \
               f"Направление обучения: {profile_data['program']}\n" + \
               f"Курс: {profile_data['course']}\n" + \
               f"Объединения: {', '.join(profile_data['unions'])}\n" + \
               f"Интересы: {', '.join(profile_data['subjects'])}\n\n" + \
               f"{profile_data['text']}"
        database.update_users(rec_user, str(call.from_user.id), 'like')
        bot.send_message(int(rec_user), text)
        offers(call)

    if call.data[:7] == 'dislike':
        rec_user = call.data[8:]
        database.update_users(rec_user, str(call.from_user.id), 'dislike')
        offers(call)

    if call.data[:10] == 'offer_skip':
        rec_user = call.data[11:]
        database.delete_user_action(rec_user, str(call.from_user.id))
        database.insert_into_actions(rec_user, str(call.from_user.id), 'send_offer')
        offers(call)

    if call.data == 'offers':
        offers(call)

    if call.data == 'help':
        help_user(call)


#УБРАТЬ В КОНЦЕ!!
@bot.message_handler(commands=['reload'])
def reload(call):
    database.delete_table('actions')
    database.create_table_actions()


bot.infinity_polling()
