import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
import database
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

bot = telebot.TeleBot('6352909336:AAGIzccUfiU-p9LGLA6R1aKtz4pecz1tjRc')
tokenizer = AutoTokenizer.from_pretrained('uaritm/multilingual_en_uk_pl_ru')
model = AutoModel.from_pretrained('uaritm/multilingual_en_uk_pl_ru')


@bot.message_handler(commands=['start'])
def start(msg):
    text = f"Привет, {msg.from_user.first_name}! \n\nЭто сервис, который помогает найти ученикам университета новые знакомства. " + \
           "Для начала работы стоит заполнить небольшую анкету."
    bot.send_message(msg.chat.id, text)
    database.delete_user(msg.chat.id)
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
           f"Интересы: {', '.join(profile_data['subjects'])}\n" + \
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
        min_sim_person = other_man.user_id[min_sim_idx]
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
        bot.register_next_step_handler(msg, get_text, profile_data)


def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Режим подбора наиболее рекомендованного пользователя", callback_data="mode_1"))
    markup.add(InlineKeyboardButton("Режим подбора пользователя по категории", callback_data="mode_2"))
    markup.add(InlineKeyboardButton("Режим подбора случайного пользователя", callback_data="mode_3"))
    markup.add(InlineKeyboardButton("Помощь", callback_data="help"),
               InlineKeyboardButton("Заполнить анкету заново", callback_data="restart"))
    markup.add(InlineKeyboardButton("Полученные анкеты", callback_data="mail"))
    return markup


@bot.message_handler(commands=['menu'])
def menu(msg):
    text = f"{msg.from_user.first_name}, что ты хочешь сделать?"
    bot.send_message(msg.chat.id, text, reply_markup=menu_markup())


def choice_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Хочу познакомиться", callback_data="accept_mode1"),
               InlineKeyboardButton("Подобрать следующего", callback_data="skip_mode1"))
    return markup


def mode_1(call):
    data_user = database.get_developer_info(str(call.from_user.id))
    df_embs = database.create_df_embs()
    rec_user = model.get_cos_sim(df_embs, str(call.from_user.id))
    data_other = database.get_developer_info(str(rec_user))
    text = f"Рекомендованный собеседник: \n\n" + \
           f"Имя: {data_other['name']}\n" + \
           f"Институт: {data_other['institut']}\n" + \
           f"Направление обучения: {data_other['program']}\n" + \
           f"Курс: {data_other['course']}\n" + \
           f"Объединения: {', '.join(data_other['unions'])}\n" + \
           f"Интересы: {', '.join(data_other['subjects'])}\n" + \
           f"{data_other['text']}"
    bot.send_message(call.from_user.id, text, reply_markup=choice_markup())
    # дописать таблицу в бд и добавление туда action


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "mode_1":
        mode_1(call)

    if call.data == 'accept_mode1':
        text = "Мы отправили этому пользователю вашу анкету, если он захочет с вами познакомиться, мы вышлем вам его контакты."
        bot.send_message(call.from_user.id, text)
        # выгружаем из actions user2 и направляем ему приглашение
        # потом добавить user2 в стоплист user1


bot.infinity_polling()
