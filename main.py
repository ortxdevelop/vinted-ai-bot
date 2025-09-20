import asyncio
from concurrent.futures import ThreadPoolExecutor

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, BaseFilter
from aiogram.types import Message

import keyboards as kb

from parser import check_vinted, start_driver, clear_seen_file

import datetime

import json

from config import *

bot = Bot(token=TG_TOKEN)

dp = Dispatcher()

executor = ThreadPoolExecutor()

class IsMe(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == int(CHAT_ID)
    
def load_times():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [tuple(t) for t in data.get("times", [])]
    except FileNotFoundError:
        return [(12, 0), (20, 0)]
    except Exception as e:
        logging.error(f"Error with loading time: {e}")
        return [(12, 0), (20, 0)]

def save_times(times):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"times": times}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error with saving time: {e}")

scheduled_times = load_times()

@dp.message(IsMe(), CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello!", reply_markup=kb.main)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello!")

@dp.message(IsMe(), Command('search'))
async def search(message: Message):
    try:
        driver = start_driver()
        status_msg = await message.answer("Searching...")
        logging.info("Search was started")

        loop = asyncio.get_event_loop()
        sent_messages = await loop.run_in_executor(executor, check_vinted, driver)

        await status_msg.delete()
        if sent_messages == 0:
            await message.answer("Nothing was found")
        msg = f"{sent_messages} message{'s' if sent_messages != 1 else ''} {'were' if sent_messages != 1 else 'was'} sent"
        logging.info(msg)
    except Exception as e:
        await message.answer(f"Error {e} was occurred")

@dp.message(Command('search'))
async def search(message: Message):
    await message.answer("You have no access")

@dp.message(IsMe(), F.text == '🔎Search')
async def search(message: Message):
    driver = start_driver()
    status_msg = await message.answer("Searching...")
    logging.info("Search was started")

    loop = asyncio.get_event_loop()
    sent_messages = await loop.run_in_executor(executor, check_vinted, driver)

    await status_msg.delete()

    if sent_messages == 0:
        await message.answer("Nothing was found")

    msg = f"{sent_messages} message{'s' if sent_messages != 1 else ''} {'were' if sent_messages != 1 else 'was'} sent"
    logging.info(msg)

@dp.message(IsMe(), Command('settime'))
async def set_time_command(message: Message):
    global scheduled_times
    try:
        parts = message.text.split()[1:]
        if not parts:
            raise ValueError
        new_times = []
        seen = set()

        for p in parts:
            h, m = p.split(":")
            h, m = int(h), int(m)
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
            
            if (h, m) in seen:
                await message.answer(f"❌ Time {h:02}:{m:02} is already set")
                return
            seen.add((h, m))
            new_times.append((h, m))

        scheduled_times = new_times
        save_times(scheduled_times)

        times_str = ", ".join([f"{h:02}:{m:02}" for h, m in scheduled_times])
        await message.answer(f"✅ New time saved: {times_str}")

    except Exception:
        await message.answer("❌ Error with message. Example: /settime 09:15 14:30 22:05")

async def scheduled_task():
    while True:
        now = datetime.datetime.now()
        if (now.hour, now.minute) in scheduled_times:
            logging.info("Starting check_vinted by time")
            driver = start_driver()
            await bot.send_message(chat_id=CHAT_ID, text=f"Scheduled search was started")
            sent_messages = check_vinted(driver)
            if sent_messages == 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"Nothing was found")

            await asyncio.sleep(60)
        await asyncio.sleep(1)

@dp.message(IsMe(), Command('clear'))
async def clear_handler(message: Message):
    status_msg = await message.answer("Clearing...")

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, clear_seen_file)

    await status_msg.delete()
    await message.answer("seen.json was cleared")

@dp.message(Command('clear'))
async def clear_handler(message: Message):
    await message.answer("You have no access")

@dp.message(IsMe(), F.text == '🗑️Clear seen.json')
async def clear_handler(message: Message):
    status_msg = await message.answer("Clearing...")

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, clear_seen_file)

    await status_msg.delete()
    await message.answer("seen.json was cleared")

@dp.message(IsMe(), F.text == '🕑Set schedule')
async def clear_handler(message: Message):
    times_str = ", ".join([f"{h:02}:{m:02}" for h, m in scheduled_times])
    await message.answer("Send a command /settime. For example: /settime 12:00 20:00")
    await message.answer(f"Current time(s): {times_str}")

async def main():
    asyncio.create_task(scheduled_task())
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")