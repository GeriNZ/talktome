# TalkToMe 🌍✨

Welcome to TalkToMe, your personal language learning assistant! With this tool, you can practice speaking, discuss articles, and get instant feedback in various languages. Currently supported languages include German, French, Italian, Spanish, and English. The best part? You can practice in real-time, without needing a partner!
The app is deployed at:
https://talktomelanguagelearning.streamlit.app/

![TalkToMe Screenshot](path_to_a_screenshot.png)  

## Features

- **Real-time Language Practice**: No need for a language partner.
- **Instant Feedback**: Get immediate feedback on your pronunciation, grammar, and usage.
- **Custom Vocabulary Tracker**: Add specific vocabulary you want to practice and track its usage during conversations.
- **Text & Voice Output**: Choose how you want to receive feedback – text, voice, or both!
- **Support for Multiple Languages**: Practice German, French, Italian, Spanish, and English.

## How to Run Locally

1. Clone this repository:

```bash
git https://github.com/GeriNZ/talktome
cd path_to_the_cloned_directory
```

## Installation and Setup

1. **Install the requirements using pipenv:**
```bash
pipenv install
```
Note: you need an **AssemblyAi** and an **OpenAI** API key to run this app locally.
Please create a config.py file and add your API keys. Make sure to uncomment the relevant lines in the code to make sure it runs locally correctly.

2. **Activate the virtual environment:**
```bash
pipenv shell
```
3. **Run the streamlit app:**
```bash
streamlit run 1_🎤_talktome.py
```
## Instructions & Tips

### How to Use:

1. **Select** your target language, proficiency level, and the kind of conversation you want (informal, formal, etc.).
2. If you have an **article or text** you want to discuss, paste it in the provided text box.
3. **Add specific vocabulary** you want to practice to the vocabulary list. The tracker will count how often you use these words.
4. **Record** your voice by pressing the microphone button, then converse freely!
5. Await the transcription and receive an **instant response** from the virtual language assistant.

### Tips for the Best Experience:

- Ensure you're in a **quiet environment**.
- Speak **clearly and at a moderate pace**.
- Use **news articles, stories, or study materials** as discussion topics.
- **Experiment and practice** as much as possible for the best results!

## Contribute

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcomed.

## Feedback

If you have any feedback or issues, please open an issue.

## License

This project is open-source and available under the MIT License.
