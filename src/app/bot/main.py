import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.app.bot.api_client import ApiClient
from src.app.bot.config import bot_settings

import logging

logger = logging.getLogger(__name__)
button_tmdb = KeyboardButton(text="Top TMDB")
button_scraper = KeyboardButton(text="Top Scraper")

keyboard_bot = ReplyKeyboardMarkup(
    keyboard=[[button_tmdb, button_scraper]],
    resize_keyboard=True,
)


def format_results(payload: dict) -> str:
    results = payload.get("results") or []
    if not results:
        return "Nothing found. Try a different query"

    lines: list[str] = []
    for i, item in enumerate(results, start=1):
        title = item.get("title", "(no title)")
        year = item.get("year")
        rating = item.get("rating")
        one_liner = item.get("one_liner") or ""
        url = item.get("tmdb_url") or ""
        genres_raw = item.get("genres") or []
        genres = ", ".join(genres_raw) if genres_raw else ""

        genres_part = f"\n{genres}" if genres else ""
        year_part = f" ({year})" if year else ""
        rating_part = f" — {rating:.1f}" if isinstance(rating, (int, float)) else ""

        lines.append(f"{i}) <b>{title}{year_part}</b>{rating_part}{genres_part}\n{one_liner}\n{url}")

    return "\n\n".join(lines)


def format_scraper_results(payload: dict) -> str:
    results = payload.get("results") or []
    if not results:
        return "Nothing found"

    lines: list[str] = []
    for i, item in enumerate(results, start=1):
        title = item.get("title", "(no title)")
        year = item.get("year")
        overview = item.get("overview") or ""
        page_url = item.get("page_url") or ""

        year_part = f" ({year})" if year else ""

        lines.append(f"{i}) <b>{title}{year_part}</b>\n{overview}\n{page_url}")

    return "\n\n".join(lines)


async def start_bot() -> None:
    bot = Bot(
        token=bot_settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    api = ApiClient(base_url=bot_settings.api_base_url)

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        logger.info("User %d started the bot", message.from_user.id if message.from_user else None)
        await message.answer(
            "Send a movie title or description. I will return up to 15 results with ratings and a one-sentence summary",
            reply_markup=keyboard_bot,
        )

    @dp.message(F.text == "Top TMDB")
    async def on_top_tmdb(message: Message) -> None:
        try:
            payload = await api.top_tmdb(limit=15)
        except Exception as e:
            await message.answer("Search Top TMDB error. Try again later")
            logger.error("Search Top TMDB error as %s", e, exc_info=True)
            return
        await message.answer(format_results(payload))

    @dp.message(F.text == "Top Scraper")
    async def on_top_scraper(message: Message) -> None:
        try:
            payload = await api.top_scraper(limit=15)
        except Exception as e:
            await message.answer("Search Top Scraper error. Try again later")
            logger.error("Search Top Scraper error as %s", e, exc_info=True)
            return
        await message.answer(format_scraper_results(payload))

    @dp.message(F.text)
    async def on_text(message: Message) -> None:
        logger.info("Search %s", message.text)
        q = (message.text or "").strip()
        if not q:
            return

        try:
            payload = await api.search(q, limit=15)
        except Exception as e:
            await message.answer("Search error. Please try again later")
            logger.error("Search error as %s", e, exc_info=True)
            return
        await message.answer(format_results(payload))

    logger.info("Start Bot")
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
