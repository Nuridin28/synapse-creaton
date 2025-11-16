import os
import asyncio
import aiohttp
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/ask")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


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


@dp.message()
async def handle_query(message: Message):
    query = message.text.strip()

    await message.answer("⏳ Выполняю запрос... Это может занять пару минут...")

    try:
        # --- FIX: используем aiohttp ---
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BACKEND_URL,
                json={"query": query},
                timeout=300     # <-- 5 минут, можно ставить больше
            ) as resp:
                resp_json = await resp.json()

        if not resp_json.get("success"):
            await message.answer(f"❌ Ошибка: {resp_json.get('error', 'Unknown error')}")
            return

        sql = resp_json.get("sql", "")
        results = resp_json.get("results", [])
        count = resp_json.get("count")
        exec_time = resp_json.get("execution_time")

        table_text = format_table(results)

        text = (
            f"<b>✅ Запрос выполнен</b>\n\n"
            f"<b>SQL:</b>\n<code>{sql}</code>\n\n"
            f"<b>Rows:</b> {count}\n"
            f"<b>Execution:</b> {exec_time} ms\n\n"
            f"<pre>{table_text}</pre>"
        )

        await message.answer(text)

    except asyncio.TimeoutError:
        await message.answer("❌ Превышено время ожидания (более 5 минут). Попробуй оптимизировать запрос.")

    except Exception as e:
        await message.answer(f"❌ Ошибка запроса:\n<code>{str(e)}</code>")


async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
