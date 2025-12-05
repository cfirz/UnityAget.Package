# UnityAgent AI Plugin

AI-powered code assistant for Unity Editor. Get intelligent code suggestions, refactoring help, and automated code generation directly in Unity.

## Features

- **AI Code Assistant**: Get suggestions and explanations for your Unity code
- **Multiple AI Providers**: Works with OpenAI (GPT-4, GPT-3.5), Claude (Opus, Sonnet, Haiku), or local LLM servers
- **Three Modes**:
  - **Chat Mode**: Ask questions and get code suggestions
  - **Agent Mode**: AI automatically modifies your files based on requests
  - **Multi-Step Mode**: Break complex tasks into steps you can review and approve
- **Smart Context**: Automatically understands your project structure and includes relevant code
- **Conversation History**: Maintains context across multiple messages
- **Real-time Streaming**: See AI responses as they're generated

## Requirements

- **Unity 6 or above**
- **API Keys**: Your own API keys from OpenAI or Anthropic (BYOK - Bring Your Own Key)
- **Proxy Server**: AWS Lambda proxy endpoint (see Setup below)
  - **Note**: Proxy not required when using Local LLM provider

## Installation

### From Unity Asset Store
1. Download the package from the Unity Asset Store
2. Import the `.unitypackage` into your Unity project
3. The plugin will appear in `Window > AI Suggestions`

### From Unity Package Manager (UPM)
1. Add the package via Git URL or scoped registry
2. The plugin will appear in `Window > AI Suggestions`

## Quick Setup

### Step 1: Configure API Keys

1. Open `Window > AI Suggestions`
2. Click the **⚙ Settings** button (top-right)
3. Enter your API keys:
   - **OpenAI API Key**: For GPT models (starts with `sk-`)
   - **Claude API Key**: For Claude models (starts with `sk-ant-`)
   - **Local LLM**: Configure if using LM Studio (no API key needed)

API keys are stored locally and never shared.

### Step 2: Set Up Proxy Server (Cloud Providers Only)

The plugin requires a proxy server to communicate with OpenAI/Claude APIs securely.

**Option A: Deploy Your Own (Recommended)**
- See `proxy/README.md` for AWS Lambda deployment instructions
- Copy the endpoint URL after deployment

**Option B: Use Existing Proxy**
- If you have a compatible proxy endpoint, enter it in Settings

**Note**: Local LLM provider connects directly to `localhost` - no proxy needed.

### Step 3: Configure Proxy URL

1. In the AI Suggestions window, enter your proxy URL
2. Or set it in Settings: `⚙ Settings > Proxy URL`

### Step 4: Start Using!

1. Select an AI provider (OpenAI, Claude, or Local)
2. Choose a model (e.g., GPT-4, Claude 3.5 Sonnet)
3. Type your question or request
4. Click **Suggest** to get AI assistance

## Basic Usage

### Chat Mode
Ask questions about your code:
- "How can I optimize this script?"
- "Explain what this code does"
- "What's the best way to implement X in Unity?"

### Agent Mode
Request automatic code changes:
- "Optimize Assets/Scripts/PlayerController.cs"
- "Add error handling to Assets/Scripts/GameManager.cs"
- "Create a new utility class for logging"

### Multi-Step Mode
Break down complex tasks:
- "Add a jump mechanic with double jump and sound effects"
- "Refactor the inventory system to use ScriptableObjects"
- The AI creates a step-by-step plan you can review before execution

### Using Code Selection
1. Select code in a Unity script editor
2. Open AI Suggestions window
3. Enable "Selected Code" and "Surrounding Lines" options
4. Ask your question - the AI will have full context

## Key Features Explained

### Smart Context System
The plugin automatically:
- Scans your project structure
- Finds relevant files based on your questions
- Includes necessary code context in prompts
- Adjusts detail level based on your needs

### Conversation History
- All conversations are saved automatically
- Access previous conversations via the History button
- Search and favorite important conversations
- Context is maintained across messages

### External Rules
Add custom rules in `Assets/UnityAgentData/Rules/`:
- Place `.txt`, `.md`, or `.text` files in the Rules folder
- Rules are automatically included in AI prompts
- Useful for project-specific coding standards
- Rules persist across package updates (stored in Assets folder, not package)

## Troubleshooting

### "Error: Proxy URL is required"
- Enter your proxy URL in Settings or the main window
- Verify the URL is correct and accessible
- **Note**: Not required for Local LLM provider

### "Error: API key is required"
- Enter your API key in Settings
- **OpenAI keys** start with `sk-`
- **Claude keys** start with `sk-ant-`
- **Local LLM** doesn't require an API key

### "HTTP 401" or Authorization Errors
- Verify your API key is valid and has credits
- Check that your proxy forwards authorization headers correctly
- For Local LLM: Ensure LM Studio is running

### "HTTP 502 Bad Gateway"
- **Most common**: Lambda timeout is too low
- **Fix**: Increase Lambda timeout to at least 120 seconds (180+ for GPT-5)
- Use Lambda Function URLs instead of API Gateway for longer timeouts

### Network Errors
- Check your internet connection (for cloud providers)
- Verify proxy URL is accessible
- For Local LLM: Ensure LM Studio is running on `http://localhost:1234`

### Settings Not Saving
- Ensure Unity has write permissions to the Assets folder
- Try manually saving: `Assets > Save`
- Check that `Assets/Editor/UnityAgent/Settings/` folder exists

## Configuration

### Model Settings
Configure default model, temperature, and max tokens in:
- `Assets/Editor/UnityAgent/Settings/AIAssistantSettings.asset`
- Or use the Settings window (⚙ button)

### Conversation History
Configure in `AIAssistantSettings.asset`:
- **Max Conversations**: How many to keep (default: 50)
- **Max History Messages**: Context size (default: 20)
- **Auto-Save**: Automatically save conversations (default: enabled)

### Context Detail Level
Choose how much code context to include:
- **Minimal**: Project summary only (fastest)
- **Summary**: Project + class outlines
- **Standard**: Project + file summaries (recommended)
- **Full**: Project + complete file contents (most context)

## Security Notes

- API keys are stored locally in `Assets/Editor/UnityAgent/.api_keys.json`
- This file is automatically excluded from git
- **Never commit API keys to version control**
- You are responsible for API usage costs from OpenAI/Anthropic

## Limitations

- **Editor-Only**: Works in Unity Editor, not in builds
- **Internet Required**: For cloud providers (OpenAI, Claude)
- **Proxy Required**: For cloud providers (not needed for Local LLM)
- **File Operations**: Agent Mode can only modify files under `Assets/` directory

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review proxy setup documentation in `proxy/README.md`
3. Verify Unity version compatibility (6.2+)

## License

This plugin is provided as-is. Use your API keys responsibly and in accordance with your provider's terms of service.

---

**Note**: This plugin acts as a bridge between Unity Editor and AI provider APIs. All AI processing happens on the provider's servers, and all costs are incurred through your provider accounts.
