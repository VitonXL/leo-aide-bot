# bot/ton_checker.py
import httpx
import logging
from datetime import datetime
from bot.database import db

# Настройка логов
logger = logging.getLogger(__name__)

# Константы
TON_API_URL = "https://toncenter.com/api/v3"
WALLET_ADDRESS = "UQCAjhZZOSxbEUB84daLpOXBPkQIWy3oB-fWoTztKdAZFDLQ"
EXPECTED_AMOUNT = 20000000  # 0.02 TON в nanotons

async def check_pending_payments(context):
    """
    Проверяет входящие транзакции на кошельке TON.
    Если найден платёж 0.02 TON с комментарием `premium:<user_id>` — выдаёт премиум-доступ.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TON_API_URL}/getTransactions",
                params={"address": WALLET_ADDRESS, "limit": 50},
                timeout=15
            )

            if response.status_code != 200:
                logger.error(f"❌ Ошибка TonCenter API: {response.status_code} — {response.text}")
                return

            transactions = response.json().get("transactions", [])
            logger.info(f"🔍 Найдено транзакций: {len(transactions)}")

            for tx in transactions:
                try:
                    # Уникальный хеш транзакции
                    tx_hash = tx["transaction_id"]["hash"]

                    # Пропускаем уже обработанные
                    if db.is_payment_processed(tx_hash):
                        continue

                    # Проверяем, что это входящий платёж
                    if tx["out_msgs"]:
                        continue

                    # Получаем сумму
                    in_msg = tx.get("in_msg")
                    if not in_msg:
                        continue

                    amount = int(in_msg["value"])

                    # Получаем комментарий
                    body = in_msg.get("decoded_body", {})
                    comment = body.get("comment", "").strip()

                    # Проверяем сумму и формат комментария
                    if amount == EXPECTED_AMOUNT and comment.startswith("premium:"):
                        try:
                            user_id = int(comment.split(":")[1])
                        except (ValueError, IndexError):
                            logger.warning(f"⚠️ Неверный формат комментария: {comment}")
                            continue

                        # Проверяем, не активен ли уже премиум
                        if db.is_premium(user_id):
                            logger.info(f"💡 Пользователь {user_id} уже имеет премиум")
                        else:
                            # Выдаём премиум на 30 дней
                            db.grant_premium(user_id, 30)
                            logger.info(f"✅ Премиум выдан пользователю: {user_id}")

                            # Отправляем уведомление
                            try:
                                await context.bot.send_message(
                                    user_id,
                                    "🎉 Оплата получена! Вам выдан премиум-доступ на 30 дней.\n"
                                    "Спасибо за поддержку! 💙"
                                )
                            except Exception as e:
                                logger.error(f"❌ Не удалось уведомить пользователя {user_id}: {e}")

                        # Отмечаем как обработанную
                        db.mark_payment_as_processed(tx_hash)

                except KeyError as e:
                    logger.error(f"❌ Некорректная структура транзакции: отсутствует {e}")
                except Exception as e:
                    logger.error(f"❌ Ошибка при обработке транзакции {tx_hash}: {e}")

    except httpx.RequestError as e:
        logger.error(f"❌ Ошибка сети при запросе к TonCenter: {e}")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка в check_pending_payments: {e}")


# === Тестовая команда (опционально) ===

async def test_ton_api(update, context):
    """Команда /test_ton — проверка подключения к API"""
    if update.effective_user.id != 1799560429:
        return

    await update.message.reply_text("🧪 Проверка подключения к TonCenter...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TON_API_URL}/getAddressInformation",
                params={"address": WALLET_ADDRESS}
            )
            if response.status_code == 200:
                data = response.json()
                balance = int(data["balance"]) / 1e9
                await update.message.reply_text(
                    f"🟢 Успешно!\nБаланс: {balance:.4f} TON\nАдрес: `{WALLET_ADDRESS}`",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(f"🔴 Ошибка API: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"🔴 Ошибка подключения: {e}")

# Чтобы использовать — добавьте в bot.py:
# application.add_handler(CommandHandler("test_ton", test_ton_api))
