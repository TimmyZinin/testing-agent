"""
Andry Tester - Telegram Bot for AI-Powered Test Generation

A Malagasy-named testing assistant that generates pytest tests
for your Python code using CrewAI multi-agent system.

Usage:
    Send Python code to the bot and receive comprehensive tests.
"""

import os
import sys
import asyncio
import tempfile
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crew import TestingCrew

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_NAME = "Andry Tester"
BOT_DESCRIPTION = "Salama! I'm Andry, your AI testing assistant from Madagascar."

# User states for conversation flow
USER_STATES = {}

# Rate limiting
RATE_LIMIT = {}
RATE_LIMIT_SECONDS = 60
MAX_REQUESTS_PER_MINUTE = 5


def get_welcome_message() -> str:
    """Return welcome message in bot's character."""
    return f"""
*{BOT_NAME}* - AI-Powered Test Generation

Salama! (Hello in Malagasy)

I'm Andry, your testing assistant. Send me Python code and I'll generate comprehensive pytest tests for you.

*Commands:*
/start - Show this welcome message
/help - Detailed help and examples
/status - Check bot and API status
/test - Start test generation mode

*Quick Start:*
Just send me any Python code and I'll analyze it and generate tests!

_Powered by CrewAI multi-agent system_
"""


def get_help_message() -> str:
    """Return detailed help message."""
    return """
*How to Use Andry Tester*

*Method 1: Direct Code*
Send Python code directly in a message:

```python
def add(a, b):
    return a + b
```

*Method 2: Code Block*
Wrap your code in markdown code blocks for better formatting.

*Method 3: File Upload*
Send a .py file and I'll generate tests for it.

*What I Generate:*
- Unit tests using pytest
- Edge case coverage
- Error handling tests
- AAA pattern (Arrange, Act, Assert)
- Descriptive test names

*Tips:*
- Larger code = longer processing
- Include docstrings for better test quality
- I work best with pure functions

*Rate Limits:*
- 5 requests per minute
- Complex code may take 1-2 minutes

Need help? Contact @TimmyZinin
"""


def check_rate_limit(user_id: int) -> tuple[bool, int]:
    """
    Check if user is rate limited.

    Returns:
        (is_allowed, seconds_until_reset)
    """
    now = datetime.now().timestamp()

    if user_id not in RATE_LIMIT:
        RATE_LIMIT[user_id] = {"requests": [], "last_reset": now}

    user_data = RATE_LIMIT[user_id]

    # Reset if minute has passed
    if now - user_data["last_reset"] > RATE_LIMIT_SECONDS:
        user_data["requests"] = []
        user_data["last_reset"] = now

    # Check limit
    if len(user_data["requests"]) >= MAX_REQUESTS_PER_MINUTE:
        seconds_left = int(RATE_LIMIT_SECONDS - (now - user_data["last_reset"]))
        return False, max(0, seconds_left)

    user_data["requests"].append(now)
    return True, 0


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        get_welcome_message(),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        get_help_message(),
        parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - check system status."""
    status_parts = ["*System Status*\n"]

    # Check API keys
    openrouter = "OPENROUTER_API_KEY" in os.environ
    groq = "GROQ_API_KEY" in os.environ
    openai = "OPENAI_API_KEY" in os.environ

    if openrouter:
        status_parts.append("LLM Provider: OpenRouter (Gemini)")
    elif groq:
        status_parts.append("LLM Provider: Groq (Llama)")
    elif openai:
        status_parts.append("LLM Provider: OpenAI (GPT-4)")
    else:
        status_parts.append("LLM Provider: Not configured")

    # Bot status
    status_parts.append(f"\nBot: Online")
    status_parts.append(f"Name: {BOT_NAME}")

    # Rate limit status for user
    user_id = update.effective_user.id
    if user_id in RATE_LIMIT:
        requests_used = len(RATE_LIMIT[user_id]["requests"])
        status_parts.append(f"\nYour requests this minute: {requests_used}/{MAX_REQUESTS_PER_MINUTE}")

    await update.message.reply_text(
        "\n".join(status_parts),
        parse_mode="Markdown"
    )


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /test command - enter test mode."""
    keyboard = [
        [InlineKeyboardButton("Send Code", callback_data="mode_code")],
        [InlineKeyboardButton("Upload File", callback_data="mode_file")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "*Test Generation Mode*\n\nHow would you like to provide your code?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "mode_code":
        USER_STATES[user_id] = "waiting_code"
        await query.edit_message_text(
            "Send me your Python code.\n\nYou can paste it directly or use markdown code blocks."
        )
    elif query.data == "mode_file":
        USER_STATES[user_id] = "waiting_file"
        await query.edit_message_text(
            "Upload a .py file and I'll generate tests for it."
        )
    elif query.data == "cancel":
        USER_STATES.pop(user_id, None)
        await query.edit_message_text("Cancelled. Send /test when you're ready!")


def extract_code_from_message(text: str) -> str:
    """Extract Python code from message, handling markdown blocks."""
    import re

    # Try to extract from markdown code blocks
    patterns = [
        r'```python\n(.*?)```',  # ```python ... ```
        r'```py\n(.*?)```',       # ```py ... ```
        r'```\n(.*?)```',         # ``` ... ```
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()

    # No code blocks, return as-is
    return text.strip()


async def generate_tests(code: str, status_message) -> Optional[str]:
    """
    Generate tests for the given code using CrewAI.

    Args:
        code: Python source code
        status_message: Telegram message to update with progress

    Returns:
        Generated test code or None on error
    """
    try:
        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_file = f.name

        await status_message.edit_text(
            "Analyzing code structure..."
        )

        # Run TestingCrew
        crew = TestingCrew()
        result = crew.run(
            file_path=temp_file,
            test_type="unit",
            test_framework="pytest",
            language="python"
        )

        # Clean up temp file
        os.unlink(temp_file)

        # Extract tests from result
        tests_content = None

        if result.get("tasks_output") and len(result["tasks_output"]) >= 2:
            tests_content = result["tasks_output"][1]
        else:
            tests_content = result.get("raw", "")

        # Extract code from markdown if present
        if tests_content:
            import re
            if "```python" in tests_content:
                code_blocks = re.findall(
                    r'```python\n(.*?)```',
                    tests_content,
                    re.DOTALL
                )
                if code_blocks:
                    tests_content = max(code_blocks, key=len)
            elif "```" in tests_content:
                code_blocks = re.findall(
                    r'```\n(.*?)```',
                    tests_content,
                    re.DOTALL
                )
                if code_blocks:
                    tests_content = max(code_blocks, key=len)

        return tests_content.strip() if tests_content else None

    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        return None


async def handle_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming code messages."""
    user_id = update.effective_user.id

    # Rate limiting
    allowed, wait_time = check_rate_limit(user_id)
    if not allowed:
        await update.message.reply_text(
            f"Rate limit reached. Please wait {wait_time} seconds."
        )
        return

    # Extract code
    text = update.message.text or ""
    code = extract_code_from_message(text)

    if not code:
        await update.message.reply_text(
            "I couldn't find any code in your message. Please send Python code."
        )
        return

    # Check if it looks like Python code
    if not any(keyword in code for keyword in ['def ', 'class ', 'import ', '=', 'return']):
        await update.message.reply_text(
            "This doesn't look like Python code. Please send valid Python code."
        )
        return

    # Send processing message
    status_msg = await update.message.reply_text(
        f"Processing your code...\n\n_This may take 1-2 minutes for complex code._",
        parse_mode="Markdown"
    )

    try:
        # Generate tests
        tests = await generate_tests(code, status_msg)

        if tests:
            # Clear user state
            USER_STATES.pop(user_id, None)

            # Send tests
            await status_msg.edit_text(
                "Tests generated successfully!"
            )

            # Split if too long for Telegram (4096 char limit)
            if len(tests) > 3500:
                # Send as file
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='_test.py',
                    delete=False,
                    encoding='utf-8'
                ) as f:
                    f.write(tests)
                    temp_file = f.name

                await update.message.reply_document(
                    document=open(temp_file, 'rb'),
                    filename="generated_tests.py",
                    caption="Here are your generated tests!"
                )
                os.unlink(temp_file)
            else:
                await update.message.reply_text(
                    f"```python\n{tests}\n```",
                    parse_mode="Markdown"
                )
        else:
            await status_msg.edit_text(
                "Sorry, I couldn't generate tests. Please check your code and try again."
            )

    except Exception as e:
        logger.error(f"Error in handle_code_message: {e}")
        await status_msg.edit_text(
            f"An error occurred: {str(e)[:200]}"
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded Python files."""
    user_id = update.effective_user.id
    document = update.message.document

    # Check if it's a Python file
    if not document.file_name.endswith('.py'):
        await update.message.reply_text(
            "Please upload a Python file (.py extension)."
        )
        return

    # Rate limiting
    allowed, wait_time = check_rate_limit(user_id)
    if not allowed:
        await update.message.reply_text(
            f"Rate limit reached. Please wait {wait_time} seconds."
        )
        return

    # Download file
    file = await context.bot.get_file(document.file_id)

    with tempfile.NamedTemporaryFile(
        mode='wb',
        suffix='.py',
        delete=False
    ) as f:
        await file.download_to_drive(f.name)
        temp_path = f.name

    # Read code
    with open(temp_path, 'r', encoding='utf-8') as f:
        code = f.read()

    os.unlink(temp_path)

    # Process like code message
    status_msg = await update.message.reply_text(
        f"Processing {document.file_name}...\n\n_This may take 1-2 minutes for complex code._",
        parse_mode="Markdown"
    )

    try:
        tests = await generate_tests(code, status_msg)

        if tests:
            USER_STATES.pop(user_id, None)

            await status_msg.edit_text("Tests generated successfully!")

            # Always send as file for uploads
            test_filename = f"test_{document.file_name}"
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(tests)
                temp_file = f.name

            await update.message.reply_document(
                document=open(temp_file, 'rb'),
                filename=test_filename,
                caption=f"Tests for {document.file_name}"
            )
            os.unlink(temp_file)
        else:
            await status_msg.edit_text(
                "Sorry, I couldn't generate tests. Please check your code and try again."
            )

    except Exception as e:
        logger.error(f"Error in handle_document: {e}")
        await status_msg.edit_text(
            f"An error occurred: {str(e)[:200]}"
        )


def main() -> None:
    """Start the bot."""
    # Get token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("Please set it with your bot token from @BotFather")
        sys.exit(1)

    # Check for LLM API keys
    if not any([
        os.getenv("OPENROUTER_API_KEY"),
        os.getenv("GROQ_API_KEY"),
        os.getenv("OPENAI_API_KEY")
    ]):
        print("Warning: No LLM API key found")
        print("Set one of: OPENROUTER_API_KEY, GROQ_API_KEY, OPENAI_API_KEY")

    # Create application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.Document.ALL, handle_document)
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_message)
    )

    # Start polling
    print(f"\n{BOT_NAME} is starting...")
    print(f"{BOT_DESCRIPTION}\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
