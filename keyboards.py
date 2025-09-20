from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = '🔎Search')],
    [KeyboardButton(text = '🗑️Clear seen.json'),KeyboardButton(text = '🕑Set schedule')],
    ],
    resize_keyboard=True
)