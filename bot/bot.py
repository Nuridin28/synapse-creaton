import os
import asyncio
import aiohttp
from dotenv import load_dotenv

import pandas as pd
import matplotlib.pyplot as plt

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/ask")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


# --------------------------
# /start
# --------------------------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "<b>👋 Привет!</b>\n\n"
        "Я аналитический бот.\n"
        "Отправь текстовый запрос — я выполню SQL и верну результат.\n\n"
        "Я могу:\n"
        "• показать таблицу\n"
        "• построить гистограмму числовых данных"
    )


# --------------------------
# Табличный вывод (ASCII)
# --------------------------
def format_table(results):
    if not results:
        return "No data"

    columns = list(results[0].keys())

    col_widths = {col: len(col) for col in columns}
    for row in results:
        for col in columns:
            col_widths[col] = max(col_widths[col], len(str(row[col])))

    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    divider = "-+-".join("-" * col_widths[col] for col in columns)

    rows = []
    for row in results:
        line = " | ".join(str(row[col]).ljust(col_widths[col]) for col in columns)
        rows.append(line)

    return header + "\n" + divider + "\n" + "\n".join(rows)


# --------------------------
# Построение гистограммы
# --------------------------
def generate_histogram(df: pd.DataFrame, output_file="histogram.png"):
    # Выбираем только числовые колонки
    numeric_cols = df.select_dtypes(include='number').columns
    if numeric_cols.empty:
        return False  # Нет числовых колонок

    plt.figure(figsize=(8, 5))
    df[numeric_cols].hist(bins=10, figsize=(8, 5))
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return True


# --------------------------
# Основная обработка текстовых запросов
# --------------------------
@dp.message()
async def handle_query(message: Message):
    query = message.text.strip()

    await message.answer("⏳ Выполняю запрос... Это может занять пару минут...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BACKEND_URL,
                json={"query": query},
                timeout=300
            ) as resp:
                resp_json = await resp.json()

        if not resp_json.get("success"):
            return await message.answer(f"❌ Ошибка: {resp_json.get('error')}")

        sql = resp_json["sql"]
        results = resp_json["results"]
        count = resp_json["count"]
        exec_time = resp_json["execution_time"]

        table_text = format_table(results)
        df = pd.DataFrame(results)

        # Отправляем таблицу
        text = (
            f"<b>✅ Запрос выполнен</b>\n\n"
            f"<b>SQL:</b>\n<code>{sql}</code>\n\n"
            f"<b>Rows:</b> {count}\n"
            f"<b>Execution:</b> {exec_time} ms\n\n"
            f"<pre>{table_text}</pre>"
        )
        await message.answer(text)

        # Построение гистограммы
        if generate_histogram(df):
            await message.answer_photo(types.FSInputFile("histogram.png"), caption="📊 Гистограмма числовых данных")
        else:
            await message.answer("ℹ️ Нет числовых колонок для построения гистограммы.")

    except Exception as e:
        await message.answer(f"❌ Ошибка:\n<code>{str(e)}</code>")


async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
