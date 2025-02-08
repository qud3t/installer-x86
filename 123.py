from hikkatl.types import Message
from .. import loader, utils  # Import utils here
import logging
import asyncio

logger = logging.getLogger(__name__)


@loader.tds
class StockroomFavoriteButtons(loader.Module):
    """Сохраняет инлайн кнопки из бота @stockroom_yt_bot в избранное."""

    strings = {
        "name": "StockroomFavoriteButtons",
        "scanning": "Сканирую сообщения в @stockroom_yt_bot на наличие инлайн кнопок...",
        "no_buttons_found": "Инлайн кнопки не найдены в @stockroom_yt_bot.",
        "buttons_saved": "Сохранил {} инлайн кнопок из @stockroom_yt_bot в избранное.",
        "error_scanning": "Произошла ошибка при сканировании сообщений: {}",
    }

    async def client_ready(self, client, db):
        """Вызывается при загрузке модуля."""
        self._client = client
        self._db = db
        self._me = await client.get_me()
        self._favorite_buttons = self.pointer("favorite_buttons", [])

    @loader.command(
        ru_doc="Сканирует @stockroom_yt_bot и добавляет инлайн кнопки в избранное.",
    )
    async def stockroomfav(self, message: Message):
        """Сканирует @stockroom_yt_bot и добавляет инлайн кнопки в избранное."""
        try:
            await utils.answer(message, self.strings("scanning"))

            bot_username = "stockroom_yt_bot"
            bot_entity = await self._client.get_entity(bot_username)
            button_count = 0

            async for msg in self._client.iter_messages(bot_entity):
                if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                    for row in msg.reply_markup.rows:
                        for button in row.buttons:
                            if hasattr(button, 'url'):
                                if button.url not in self._favorite_buttons:
                                    self._favorite_buttons.append(button.url)
                                    button_count += 1
                            elif hasattr(button, 'callback_data'): # check for callback data instead of url
                                data_str = button.callback_data.decode("utf-8")
                                if data_str not in self._favorite_buttons:
                                    self._favorite_buttons.append(data_str)
                                    button_count += 1

            if button_count == 0:
                await utils.answer(message, self.strings("no_buttons_found"))
            else:
                await utils.answer(message, self.strings("buttons_saved").format(button_count))

        except Exception as e:
            logger.exception("Error scanning @stockroom_yt_bot:")
            await utils.answer(message, self.strings("error_scanning").format(str(e)))

    @loader.command(
        ru_doc="Показывает сохраненные инлайн кнопки из избранного.",
    )
    async def showfav(self, message: Message):
      """Показывает сохраненные инлайн кнопки из избранного."""
      buttons = self._favorite_buttons or []

      if not buttons:
        await utils.answer(message, "No saved buttons found.")
        return

      output = "Сохраненные Избранные Кнопки:\n"
      for i, button in enumerate(buttons):
        output += f"{i + 1}. {button}\n"

      await utils.answer(message, output)
