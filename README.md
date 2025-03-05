# Pennyworth Slack Bot

## Overview

A versatile Slack bot with AI assistance, Trello integration, and team management features.

<br>

## Features
- New user onboarding notifications
- AI-powered chat assistance
- Trello workflow management

<br>

## Initial Set-Up

```bash
# Create conda environment
conda create -n pennyworth python=3.11
conda activate pennyworth

# Create project directory
mkdir pennyworth-slack-bot
cd pennyworth-slack-bot

# Initialize git repository
git init
```

<br>

## Dependencies

```bash
# Install required packages
pip install slack-bolt google-generativeai trello-py python-dotenv

# Generate requirements.txt
pip freeze > requirements.txt
```

<br>

## File Structure

```bash
pennyworth-slack-bot/
│
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main Slack bot logic
│   ├── ai_assistant.py     # Gemini AI integration
│   ├── trello_workflows.py # Trello workflow handlers
│   ├── secrets.py          # Bitwarden secret management
│   └── utils/              # Utility modules
│       └── __init__.py
│
├── .env                    # Environment variables (local fallback)
├── requirements.txt        # Project dependencies
└── main.py                 # Application entry point
```
