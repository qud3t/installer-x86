from hikkatl.types import Message
from .. import loader
import asyncio


@loader.tds
class AutoBonusModule(loader.Module):
    """Автоматически отправляет сообщение о бонусе в указанный чат."""
    strings = {
        "name": "AutoBonus",
        "bonus_message": "🎁 Бонус",
        "no_chat_id": "Укажите chat_id для отправки сообщений.",
        "invalid_chat_id": "Неверный chat_id. Проверьте идентификатор чата.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "chat_id",
                None,
                "ID чата, куда отправлять сообщения. Оставьте пустым, чтобы отключить.",
                validator=loader.validators.TelegramID(),  # Используем TelegramID валидатор
            )
        )

    async def client_ready(self):
        """Вызывается, когда Telegram клиент готов к работе."""
        self.chat_id = self.config["chat_id"]
        if self.chat_id:
            asyncio.create_task(self.bonus_loop())

    async def bonus_loop(self):
        """Циклическая задача для отправки сообщения о бонусе."""
        while True:
            if not self.chat_id:
                self.log.debug("chat_id не задан. Цикл остановлен.")
                return

            try:
                await self._client.send_message(self.chat_id, self.strings("bonus_message"))
                self.log.info(f"Отправлено сообщение о бонусе в {self.chat_id}")
            except Exception as e:
                self.log.error(f"Ошибка при отправке сообщения: {e}")
                # Проверяем, является ли ошибка неверным chat_id
                if "chat_id invalid" in str(e):
                    self.log.error(self.strings("invalid_chat_id"))
                    self.chat_id = None  # Отключаем отправку, если chat_id неверный
                    self.config["chat_id"] = None
                    return #Завершаем цикл

            await asyncio.sleep(60 * 60)  # Пауза на 1 час (3600 секунд)

    @loader.command(
        ru_doc="Установить/проверить chat_id для отправки сообщений о бонусах",
        alias="setbonuschat"
    )
    async def bonuschat(self, message: Message):
      """Установить/проверить chat_id для отправки сообщений о бонусах"""
      args = utils.get_args_raw(message)
      if args:
        try:
          chat_id = int(args)
          self.config["chat_id"] = chat_id
          self.chat_id = chat_id #обновляем chat_id для работы bonus_loop
          await message.edit(f"chat_id установлен на {chat_id}. Перезапустите модуль для применения.")
          if not asyncio.current_task().done():
            asyncio.create_task(self.bonus_loop())
        except ValueError:
          await message.edit("Неверный chat_id. Должно быть целым числом.")
        except Exception as e:
          await message.edit(f"Ошибка: {e}")
      else:
        if self.chat_id:
          await message.edit(f"Текущий chat_id: {self.chat_id}")
        else:
          await message.edit(self.strings("no_chat_id"))
