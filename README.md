<p align="center">
  <h1 align="center">FlashMindsBot</h2>

<p align="center">
  <img src="./assets/logo.jpeg" width="250px" height="250px">
</p>

FlashMinds revolutionizes the way you learn by combining the simplicity of flashcards with the power of artificial intelligence. In addition to traditional flashcard functionality, FlashMinds employs advanced AI algorithms to enhance your learning experience.

[gif]

## Table of contents
- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contributors](#contributors)

## Introduction

Welcome to FlashMinds, where learning meets innovation! Our Telegram Bot redefines the learning experience by seamlessly integrating the simplicity of flashcards with the transformative power of artificial intelligence. Explore a new dimension of learning with these features:

1. **Smart Flashcards** <br>
Create flashcards effortlessly using our innovative generator. Simply send an image containing text to the bot, and it will generate a question-answer pair based on the image content. Alternatively, you can manually input questions and answers. 

2. **AI-Powered** <br>
Leverage advanced AI algorithms that analyze your progress and suggest tailored study materials. In study mode, FlashMinds utilizes ChatGPT to dynamically generate questions based on your saved card. This ensures varied questions while covering the same material, providing a diverse learning experience. Additionally, our algorithm identifies questions that students typically find challenging at the beginning of a session, helping you focus on areas that need attention.

- **Interactive Quizzes** <br>
 In study mode, students can view a question, reveal the answer, and self-assess their response. This interactive process enhances the learning experience, allowing for immediate reflection and improvement.

- **Progress Tracking** <br>
Keep tabs on your learning journey. FlashMinds provides insights into your progress, helping you identify strengths and areas for improvement.

- **Cross-Platform Accessibility** <br>
Access your study materials anytime, anywhere with the convenience of Telegram. FlashMinds is accessible through any Telegram app, whether on mobile or desktop. Seamlessly pick up where you left off and continue your learning journey effortlessly.


## Documentation
Explore and test the API using our Postman Collections:
- [CHAT GPT API](https://documenter.getpostman.com/view/31304624/2s9YeN3Uz2)
- [FLASHCARD API](https://documenter.getpostman.com/view/31304624/2s9YeN3V4K)
- [OCR API](https://documenter.getpostman.com/view/31304624/2s9YeN3V4M)
- [SCHEDULER API](https://documenter.getpostman.com/view/31304624/2s9YeN3V4N)

These collections includes pre-configured requests for various endpoints, making it easier to interact with the APIs.

## Getting Started
Before you get started,
1. Get your [OpenAI API](https://openai.com/product) key
2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

### Prerequisites
Make sure you have Docker and Docker Compose installed on your machine.
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

## Usage
To run this project, you can use Docker and Docker Compose. Follow these steps:
1. Clone the repository to your local machine.
```bash
git clone https://github.com/glonor/flashminds
cd flashminds
```

1. Create a .env file in the project root and configure these variables:
```
#Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

#ChatGPT 3.5 API
CHATGPT_API_KEY=your_chatgpt_api_key_here
```

Make sure not to share or commit your .env file to keep your sensitive information private. 

2. Build and run the project using Docker Compose.
```bash
docker-compose up --build
```
This command will build the Docker images and start the containers based on the configuration in the docker-compose.yml file.

3. Access your Telegram Bot.
Once the containers are running, you can access your FlashMindsBot via Telegram.


## Contributing
If you'd like to contribute to FlashMindsBot, please follow these guidelines:

1. Fork the repository to your GitHub account.
2. Clone the forked repository to your local machine.

```bash
git clone https://github.com/your-username/repository.git
```
3. Create a new branch for your contribution.
```bash
git checkout -b feature/your-feature
```
4. Create a new branch for your contribution.
```bash
git checkout -b feature/your-feature
```
5. Make your changes in the new branch. Ensure that your code follows the project's coding standards.
6. Test your changes thoroughly to make sure they work as expected.
7. Commit and push your changes.
```bash
git commit -m "Add your meaningful commit message"
git push origin feature/your-feature
```
8. Open a pull request on the original repository. Provide a clear and concise description of your changes.

## Contributors

![GitHub contributors](https://img.shields.io/github/contributors/glonor/flashminds?style=for-the-badge)

