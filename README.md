# Pennyworth Slack Bot

## Overview

Pennyworth is an elegant Slack assistant that combines AI capabilities, Trello integration, and team management features into a helpful digital butler. Styled after Batman's faithful companion Alfred Pennyworth, the bot responds with formal, dignified replies while providing useful functionality for your team.

<br>

![pennyworth-slackbot-scrnshot](https://github.com/user-attachments/assets/72ca12c0-f412-42c1-bff6-a07940218cca)

<br>

## Features

**AI-Powered Assistance**
- Natural language responses using Google Gemini AI
- Contextual chat memory with persona-based responses
- Command prefix (`!ai`) for direct AI queries

**Trello Workflow Management**
- Create and manage cards with `!trello` commands
- Move cards between lists
- Add comments to cards
- List available boards and lists

**Team Management**
- Personalized new user onboarding
- Automated welcome messages
- Conversation summarization
- Response to mentions in channels

**Slack Integration**
- Socket Mode connectivity
- Direct message interactions
- Channel mentions with `@Pennyworth`
- Message commands with prefix (`!command`)

<br>

## Architecture
```bash
┌─────────────────┐      ┌───────────────┐      ┌───────────────┐
│                 │      │               │      │               │
│  Slack Platform ├──────┤  Cloud Run    ├──────┤  Google       │
│                 │      │  Container    │      │  Gemini AI    │
└─────────────────┘      └──────┬────────┘      └───────────────┘
                                │
                                │
                         ┌──────┴────────┐
                         │               │
                         │  Trello API   │
                         │               │
                         └───────────────┘
```

<br>

## Required Resources

#### Cloud Infrastructure
- **Google Cloud Platform**
    - Cloud Run service
    - Container Registry (GCR or Artifact Registry)
    - Service Account with proper permissions

#### API Keys & Tokens
- **Google Cloud Platform**
    - Bot Token (`xoxb-*`) - Required for posting messages
    - App Token (`xapp-*`) - Required for Socket Mode
    - Signing Secret - For request verification
- **Google Cloud Platform**
    - API Key
    - API Secret
    - Token
- **Google AI**
    - Gemini API Key

#### GitHub
- **GitHub CLI Authentication** (for semantic release)
    - Personal access token with `repo` scope
    - SSH key for Git operations (optional)

<br>

## Slack App Setup

1. Create a Slack App
    1. Go to [api.slack.com/apps]
    2. Click "Create New App" and choose "From scratch"
    3. Name your app "Pennyworth" and select your workspace

2. Configure Bot User
    1. Navigate to "App Home"
    2. Enable "Always Show My Bot as Online"
    3. Enable "Messages Tab"
    4. Check "Allow users to send messages in the app home"

3. OAuth & Permissions
    1. Go to **"OAuth & Permissions"**
    2. Add these _Bot Token Scopes:_
        - `app_mentions:read`       - Detect @mentions of your bot
        - `channels:history`        - Read messages in public channels
        - `channels:join`           - Join public channels
        - `channels:read`           - View public channels
        - `chat:write`              - Send messages
        - `chat:write.public`       - Send messages to public channels
        - `groups:history`          - Read messages in private channels
        - `groups:read`             - View private channels
        - `im:history`              - Read direct messages
        - `im:read`                 - View direct messages
        - `im:write`                - Send direct messages
        - `mpim:history`            - Read group direct messages
        - `mpim:read`               - View group direct messages
        - `mpim:write`              - Send group direct messages
        - `reactions:read`          - View reactions
        - `reactions:write`         - Add/remove reactions
        - `team:read`               - View basic team info
        - `users:read`              - View user profiles
        - `users:read.email`        - View email addresses
    
    3. Add these _User Token Scopes:_
        - `chat:write:user`         - Send messages as user
        - `users.profile:read`      - View user profiles in detail

4. Event Subscriptions
    1. Go to **"Event Subscriptions"** and enable
    2. Subscribe to these _bot events:_
        - `app_mention`             - When someone @mentions your bot
        - `message.channels`        - Messages in public channels
        - `message.groups`          - Messages in private channels
        - `message.im`              - Direct messages to your bot
        - `message.mpim`            - Messages in group DMs with your bot
        - `team_join`               - When new users join the workspace
        - `channel_created`         - When a channel is created
        - `channel_archive`         - When a channel is archived
        - `channel_unarchive`       - When a channel is unarchived
        - `member_joined_channel`   - When users join a channel
        - `member_left_channel`     - When users leave a channel
    
5. Socket Mode
    1. Go to "Socket Mode" and enable
    2. Create an app-level token with `connections:write` scope
    3. Note the token starting with `xapp-`

6. Install to Workspace
    1. Go to "Install App"
    2. Click "Install to Workspace" and authorize

<br>

## Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/pennyworth-slack-bot.git
cd pennyworth-slack-bot

# Create conda environment
conda create -n pennyworth python=3.11
conda activate pennyworth

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your secret tokens
```

<br>

## Environment Variables
```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# Trello Configuration
TRELLO_API_KEY=your-trello-key
TRELLO_API_SECRET=your-trello-secret
TRELLO_TOKEN=your-trello-token

# Google AI Configuration
GOOGLE_GEMINI_API_KEY=your-gemini-key

# Application Configuration
TIMEZONE=America/New_York
LOG_LEVEL=INFO
```

<br>

## File Structure
```bash
pennyworth-slack-bot/
│
├── src/                     # Source code directory
│   ├── __init__.py          # Version information
│   ├── bot.py               # Main Slack bot logic
│   ├── ai_assistant.py      # Gemini AI integration
│   ├── trello_workflows.py  # Trello workflow handlers
│   └── utils/               # Utility modules
│       └── __init__.py
│
├── server.py                # Cloud Run server & health checks
│
├── .github/                 # GitHub Actions workflows
│   └── workflows/
│       ├── slack-bot-deploy.yml    # Main deployment workflow
│       └── py-semantic-release.yml # Versioning workflow
│
├── .env.example             # Example environment variables
├── Dockerfile               # Container definition
├── requirements.txt         # Project dependencies
├── pyproject.toml           # Semantic versioning config
├── CHANGELOG.md             # Automatically generated changelog
└── README.md                # Project documentation
```

<br>

## Deployment Guide

#### Local Development Testing
```bash
# Export your GitHub token for semantic-release
export GH_TOKEN=$(gh auth token)

# Update version based on conventional commits
semantic-release version

# Run the bot locally
python server.py
```

#### Cloud Deployment

The project uses GitHub Actions for CI/CD:

1. Push changes to the main branch
2. The py-semantic-release workflow updates version and changelog
3. The slack-bot-deploy workflow:
    - Builds a Docker container
    - Pushes to GitHub Container Registry
    - Copies to Google Container Registry
    - Deploys to Cloud Run
    - Sends notification to Slack

#### Manual Deployment
```bash
# Build container
docker build -t pennyworth-bot:latest .

# Test locally
docker run -p 8080:8080 --env-file .env pennyworth-bot:latest

# Deploy to Cloud Run
gcloud run deploy pennyworth-bot \
  --image gcr.io/your-project/pennyworth-bot:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

<br>

## Usage Guide

#### Direct Messages

Start a conversation with Pennyworth in DMs:
- `hello` - Get a greeting
- `!ai [question]` - Ask AI a question
- `!summarize` - Summarize recent conversation
- `!trello` boards - List available Trello boards

#### Channel Interactions

Add Pennyworth to a channel and:
- `@Pennyworth [question]` - Mention to ask a question
- `!ai [question]` - Use the AI command
- `!trello create [title] in [list]` - Create a Trello card

<br>

## Troubleshooting

#### Slack Connection Issues
- Verify Socket Mode is enabled
- Check that event subscriptions are configured
- Confirm the app tokens start with `xoxb-` and `xapp-`
- Look at Cloud Run logs for connection errors

#### Message Response Issues
- Ensure the bot is added to the channel
- Check event subscriptions include `app_mention` and `message.*`
- Verify the bot has proper OAuth scopes
- Inspect Cloud Run logs for any errors

#### Container Deployment Issues
- Check the GitHub Actions workflow logs
- Verify environment variables are correctly set
- Ensure service account has proper permissions

<br>

## Contributing

Please follow [Conventional Commits](https://www.conventionalcommits.org/) format for all commits to ensure proper semantic versioning:
- `feat: add new feature` (triggers minor version bump)
- `fix: resolve bug` (triggers patch version bump)
- `docs: update documentation` (no version bump)
- `chore: update dependencies` (no version bump)
