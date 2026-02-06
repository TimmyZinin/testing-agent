# Andry Tester Bot Setup

## Quick Setup (5 минут)

### 1. Создание бота в Telegram

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду: `/newbot`
3. Имя бота: `Andry Tester`
4. Username бота: `andry_tester_bot` (или другой свободный)
5. Скопируйте токен бота (выглядит как `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Настройка окружения

```bash
# Экспортируйте токен
export TELEGRAM_BOT_TOKEN="ваш_токен_здесь"

# Также нужен ключ LLM (один из)
export OPENROUTER_API_KEY="ваш_ключ"
# или
export GROQ_API_KEY="ваш_ключ"
```

### 3. Запуск бота

```bash
cd /Users/timofeyzinin/Library/CloudStorage/GoogleDrive-tim.zinin@gmail.com/My\ Drive/СБОРКА/testing-agent
source .venv12/bin/activate
python -m bot.telegram_bot
```

## Настройка бота в BotFather (опционально)

После создания бота, отправьте эти команды @BotFather:

```
/setdescription
```
Описание:
```
Salama! I'm Andry, your AI-powered testing assistant from Madagascar. Send me Python code and I'll generate comprehensive pytest tests for you.
```

```
/setabouttext
```
About:
```
AI Test Generator powered by CrewAI. Generates pytest tests for Python code.
```

```
/setcommands
```
Команды:
```
start - Show welcome message
help - Get detailed help
test - Start test generation mode
status - Check bot and API status
```

## Деплой на Railway

1. Создайте новый проект на Railway
2. Подключите GitHub репозиторий
3. Добавьте переменные окружения:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENROUTER_API_KEY` (или другой LLM ключ)
4. Railway автоматически задеплоит бота

## Использование

1. Найдите бота в Telegram: @andry_tester_bot
2. Отправьте `/start`
3. Отправьте Python код
4. Получите сгенерированные тесты!

## Troubleshooting

**Бот не отвечает:**
- Проверьте `TELEGRAM_BOT_TOKEN`
- Проверьте логи: `python -m bot.telegram_bot 2>&1`

**Ошибка генерации тестов:**
- Проверьте LLM API ключ
- Отправьте `/status` для диагностики

**Rate limit:**
- Максимум 5 запросов в минуту
- Подождите и попробуйте снова
