# FlashMinds

FlashMinds revolutionizes the way you learn by combining the simplicity of flashcards with the power of artificial intelligence. In addition to traditional flashcard functionality, FlashMinds employs advanced AI algorithms to enhance your learning experience.

<img title="a title" alt="FlashMinds" src="assets/header.png">

## Key Features:

- **Smart Flashcards**: Create and study smart flashcards that adapt to your learning progress. FlashMinds intelligently adjusts the scheduling of cards based on your performance, ensuring an optimal learning experience.

- **Dynamic Wording**: FlashMinds utilizes ChatGPT to dynamically generate variations of flashcards with different wording. This ensures that you encounter the same concept presented in various ways, reinforcing your understanding and promoting a deeper comprehension.

- **Automated Flashcard Generation from Images**: Seamlessly transform pictures with textual content into flashcards using AI. 

- **Telegram Bot**: Access your flashcards directly through Telegram. With our intuitive Telegram bot, studying becomes as simple as sending a message.

## How It Works:

1. Create Decks: Build your own flashcard decks.

2. Study Efficiently: Use the spaced repetition algorithm to optimize your study sessions. Focus on the flashcards that need more attention, helping you memorize information more effectively.

## Configuration Setup
 - Obtain your [OpenAI API key](https://platform.openai.com/docs/api-reference) and [Telegram Bot token](https://core.telegram.org/bots/api) to proceed.

 - Create a .env file in the project root directory.

 - Add the following lines to your .env file, replacing OPENAI_API_KEY and TELEGRAM_BOT_API_TOKEN with your actual keys:

```
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_API_TOKEN=your_telegram_api_token_here
```

## Running the Application
Build and run the containers in daemon mode using the following command:

```
docker-compose up -d --build
```

## API Documentation

TODO
