from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


ordbut = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='💳 Click'),
            KeyboardButton(text='💵 Naqd')
        ],
        [
            KeyboardButton(text='⬅️ Orqaga')
        ],
    ],
    resize_keyboard=True
)

ordbut_rus = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='💳 Click'),
            KeyboardButton(text='💵 Наличные')
        ],
        [
            KeyboardButton(text='⬅️ Назад')
        ],
    ],
    resize_keyboard=True
)


delevery = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🏫 Olib ketish'),
            KeyboardButton(text='🛵 Yetkazib berish')
        ],
        [
            KeyboardButton(text='⬅️ Orqaga')
        ],
    ],
    resize_keyboard=True
)

delevery_rus = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🏫 Самовывоз'),
            KeyboardButton(text='🛵 Доставка')
        ],
        [
            KeyboardButton(text='⬅️ Назад')
        ],
    ],
    resize_keyboard=True
)

checkbutton = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='✅ Buyurtmani tasdiqlash')
        ],
        [
            KeyboardButton(text='💬 Buyurtmaga kommentariy')
        ],
        [
            KeyboardButton(text='⬅️ Orqaga'),
            KeyboardButton(text='❌ Bekor qilish')

        ],
    ],
    resize_keyboard=True
)


checkbutton_rus = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='✅ Подтвердить заказ')
        ],
        [
            KeyboardButton(text='💬 Комментарий к заказу')
        ],
        [
            KeyboardButton(text='⬅️ Назад'),
            KeyboardButton(text='❌ Отмена')

        ],
    ],
    resize_keyboard=True
)


comback = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='⬅️ Orqaga')

        ],
    ],
    resize_keyboard=True
)

comback_rus = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='⬅️ Назад')

        ],
    ],
    resize_keyboard=True
)

location = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📍Lokatsiya yuborish', request_location=True)

        ],
        [
            KeyboardButton(text='⬅️ Orqaga')

        ],
    ],
    resize_keyboard=True
)

location_rus = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📍Отправить Локатцию', request_location=True)

        ],
        [
            KeyboardButton(text='⬅️ Назад')

        ],
    ],
    resize_keyboard=True
)

number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📲 Telefon raqamni yuborish', request_contact=True)

        ],
        [
            KeyboardButton(text='⬅️ Orqaga')

        ],
    ],
    resize_keyboard=True
)

number_rus = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📲 Отправить номер телефона', request_contact=True)

        ],
        [
            KeyboardButton(text='⬅️ Назад')

        ],
    ],
    resize_keyboard=True
)