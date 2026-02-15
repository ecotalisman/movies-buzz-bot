import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.app.bot.api_client import ApiClient
from src.app.bot.config import bot_settings

import logging

logger = logging.getLogger(__name__)


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
            "Send a movie title or description. I will return up to 10 results with ratings and a one-sentence summary"
        )

    @dp.message(F.text)
    async def on_text(message: Message) -> None:
        logger.info("Search %s", message.text)
        q = (message.text or "").strip()
        if not q:
            return

        try:
            payload = await api.search(q, limit=10)
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
