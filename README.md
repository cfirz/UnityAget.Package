# UnityAgent AI Plugin
<img width="2528" height="1696" alt="card" src="https://github.com/user-attachments/assets/cc3cf363-ad5d-4b4b-8834-9307de472a3d" />

*AI-powered code assistant for the Unity Editor.* 
UnityAgent integrates intelligent code suggestions and automation into your Unity workflow. 
It can analyze your C# scripts and project context to offer helpful refactoring tips, debug assistance, and even generate or modify code for you. 
You remain in charge at all times - you use your own API keys, choose which AI model to work with (including local models), and control how much context is sent to the AI. 
In short, it's like having a smart pair-programmer inside Unity **on your terms**.

## Features

- **AI Code Assistant**: Get on-demand suggestions and explanations for your Unity C# code, right in the Editor.
- **Multiple AI Providers**: Works with OpenAI (GPT-4, GPT-3.5), Anthropic Claude (Opus, Sonnet, Haiku), or even local LLMs. You have the freedom to choose the model that best fits your needs – including offline local models – rather than being tied to a single AI service.
- **Bring Your Own API Key (BYOK)**: Use your personal API keys from OpenAI or Anthropic. There are no third-party subscriptions or charges; all usage is through your own accounts, giving you transparency and control over costs.
- **Adjustable AI Usage**: Configure how much code context to include in AI prompts (from brief summaries to full code). This lets you manage token usage for each request, balancing detail vs. cost so you have full control over how the AI is used.
- **Three Modes**: Flexible ways to interact with the AI assistant:
  - **Chat Mode** – Ask general questions and get coding help in a conversational format.
  - **Agent Mode** – Have the AI automatically apply changes to your project files based on your requests (create, edit, or delete files under `Assets/`). Tackle complex tasks by letting the AI propose a step-by-step plan that you can review and approve before execution.
- **Smart Context**: Automatically understands your project structure and finds relevant code to include as context. UnityAgent scans your project for related classes or scripts and can include surrounding code or project summaries to improve answer quality.
- **Conversation History**: Maintains context across multiple messages. All your AI conversations are saved so you can refer back to them, search them, or mark favorites. The context of previous messages is preserved to provide continuity.
- **Real-Time Streaming**: See AI responses live as they are generated, so you don't have to wait for the entire answer to finish. This streaming feedback makes the assistant feel responsive and interactive.

## Requirements

- **Unity**: Version 6 or above (Unity 2023.2+)
- **For Local Use**: 
  - **LM Studio** – Install [LM Studio](https://lmstudio.ai/) and load a preferred local model (if you want to use a local LLM instead of cloud services).
- **For Cloud APIs**: 
  - **API Keys** – Your own API keys for OpenAI and/or Anthropic (Bring Your Own Key).
  - **Proxy Server** – An endpoint to forward API requests (AWS Lambda proxy recommended; see setup below).

*Note:* You can use UnityAgent with either a **local** model or a **cloud** AI provider. If you're not using a local LLM, make sure you have an API key (and a proxy set up) for at least one cloud provider (OpenAI or Anthropic).

## Installation

### Option 1: Unity Asset Store (`.unitypackage`)

1. **Download the plugin** – Get the UnityAgent package from the Unity Asset Store (or from this repo’s GitHub Releases page).
2. **Import into Unity** – In Unity, go to **Assets > Import Package > Custom Package...** and select the downloaded `.unitypackage` file. Unity will import the plugin files.
3. **Open the Plugin Window** – After import, the tool will be available under **Window > AI Assistant** in the Unity Editor.

### Option 2: Unity Package Manager (Git URL)

1. Open Unity and go to **Window > Package Manager**.
2. Click the **+** button and choose **Add package from git URL...**.
3. Enter the repository URL: `https://github.com/cfirz/UnityAget.Package.git` and click **Add**. Unity will download and install the package.
4. Once installation is complete, find the tool under **Window > AI Assistant** in the Unity Editor.

## Quick Setup

After installing the plugin, follow these steps to configure it:

### Step 1: Enter Your API Keys

1. Open the **AI Assistant** window via **Window > AI Assistant**.
2. Click the **⚙ Settings** button (gear icon in the top-right of the AI Assistant panel).
3. Enter your API keys:
   - **OpenAI API Key** – for GPT models (your key starting with `sk-...`).
   - **Anthropic Claude API Key** – for Claude models (key starting with `sk-ant-...`).
   - **Local LLM** – if using a local model via LM Studio, specify the model name (no API key required).
4. *Security:* Your API keys are stored locally on your machine and never shared.

### Step 2: Set Up a Proxy (Cloud providers only)

The plugin communicates with OpenAI/Claude through a proxy server (this is required because the Unity Editor cannot directly handle the API's streaming responses). If you plan to use cloud AI providers, set up one of the following:

- **Option A: Deploy Your Own Proxy (Recommended)** – Use our AWS Lambda setup for a secure proxy:
  - Follow the instructions in the included `Proxy/PROXY_SETUP_GUIDE.md` to deploy a proxy on AWS Lambda.
  - (For testing, see `Proxy/LAMBDA_TESTING_GUIDE.md`.)
  - A ready-to-use Lambda function is provided in `Proxy/lambda_function.py` – you can deploy this function via AWS. Once deployed, note the function’s **URL endpoint**.
- **Option B: Use an Existing Proxy** – If you already have an API proxy that meets the requirements (accepts `POST /suggest` and forwards requests with `Authorization: Bearer <API_KEY>` header, returning streaming responses), you can use its URL directly.

**Note:** A proxy is **not** needed for local LLM usage. UnityAgent connects to LM Studio on your machine (http://localhost) directly.

**Note:** After installing the package, you can find the proxy setup guides and the Lambda function code inside the plugin's `Proxy/` folder. For example, with a UPM installation look under **Packages/com.cfirz.unityagent/Proxy/**, or under **Assets/UnityAgent/Proxy/** if you imported via unitypackage.

### Step 3: Configure the Proxy URL

Once your proxy is ready (for OpenAI/Claude users):

1. In the **AI Assistant** window, enter the proxy endpoint URL you obtained.
2. Alternatively, you can open the Settings again (⚙) and set the **Proxy URL** there. (The URL will be saved in the plugin’s settings asset for future use.)

### Step 4: Start Using UnityAgent!

With keys (and proxy, if needed) configured, you're ready to go:

1. In the AI Assistant window, select an AI Provider from the drop-down (e.g. **OpenAI**, **Claude**, or **Local**).
2. Choose a specific Model (for example, GPT-4 or Claude 2, or the name of your local model).
3. Type a question or request in the prompt area.
4. Click the **Submit** button. The AI will process your request and stream the answer right in the Unity Editor.

You can now get AI help directly as you develop – try asking for a suggestion or explanation about a piece of code, or let the Agent do it by himself!

## Basic Usage

UnityAgent offers multiple modes to assist you:

### Chat Mode

Use Chat Mode to ask general questions or get explanations about your code without making changes.

- *Example:* "How can I optimize this script for better performance?"
- *Example:* "Explain what this `PlayerController` code is doing."
- *Example:* "What's a good way to implement a singleton pattern in Unity?"

### Agent Mode

#### Agent Mode allows the AI to make changes to your project automatically based on your instructions. The plugin will create, edit, or delete files under your `Assets/` folder as needed.

- *Example:* "Optimize the script at **Assets/Scripts/PlayerController.cs**."
- *Example:* "Add null-checking to **Assets/Scripts/GameManager.cs** for all public methods."
- *Example:* "Create a new script **Assets/Scripts/Logging/Logger.cs** with a static logging class."

#### Agent Multi-Step Mode breaks down complex tasks into a sequence of steps. The AI will propose a plan, and you can approve each step before it runs (great for larger features or refactoring).

- *Example:* "Add a double-jump feature to the player, including sound effects and particle effects."
- *Example:* "Refactor the inventory system to use ScriptableObjects instead of enums."
- *How it works:* The AI will outline a plan (step 1, step 2, step 3, ...). You review the plan and approve steps one by one. This lets you catch any issues or modifications before the AI applies them.

## Key Features Explained

### Smart Context System

UnityAgent’s context system intelligently includes relevant parts of your project in AI prompts:
- Scans your project structure and builds a knowledge base of your scripts/classes.
- Automatically finds and injects relevant code or file snippets based on your question.
- Ensures the AI has the necessary context (e.g., related classes or definitions) to answer accurately.
- You can configure the **context detail level** (Minimal, Summary, Standard, Full) to control how much project code is sent to the AI.

### Conversation History

- Every conversation you have is saved automatically. This means the AI remembers earlier parts of the discussion within the session.
- You can revisit past conversations using the **History** button in the AI Assistant window.
- A search function lets you find key discussions, and you can "favorite" important conversation threads for quick access.
- The context of previous messages in a conversation is maintained, so the AI can refer back to what you’ve already discussed.

### External Rules

You can provide custom guidelines or rules that the AI will always consider:
- In your project, navigate to **Assets/UnityAgentData/Rules/**.
- Add any `.txt`, `.md`, or `.text` files here. Each file’s content will be treated as a rule or note for the AI.
- These rules are automatically included in the AI's system prompts (no extra setup needed).
- Use this for project-specific conventions, coding standards, or important notes (e.g. "always use our custom Logger class for logging").
- **Persistence:** The Rules folder is in your project Assets (not inside the package), so your custom rules stay intact even if you update or re-import the UnityAgent plugin.

## Troubleshooting

Having an issue? Here are common problems and solutions:

### "Error: Proxy URL is required"

- This error means the plugin doesn't know where to send API requests. Go to Settings (⚙) or the main AI Assistant window and enter your proxy URL.
- Double-check that the URL you entered is correct and reachable.
- **Note:** You do *not* need a proxy URL if you're only using a local LLM provider.

### "Error: API key is required"

- You need to input an API key for the AI service you're trying to use. Open Settings and enter the required key.
- For **OpenAI**, the key should start with `sk-...`
- For **Claude (Anthropic)**, the key typically starts with `sk-ant-...`
- **Local LLM** mode does not require any API key (just ensure LM Studio is running).

### "HTTP 401" or other Authorization Errors

- A 401 usually means something is wrong with authentication. Verify that you copied your API key correctly and that it’s active (has credits/quota).
- If using a proxy, make sure your proxy is forwarding the `Authorization` header to the AI service properly (the proxy setup guide covers this).
- For Local LLM usage, ensure that LM Studio is up and running (so the plugin can reach it).

### "HTTP 502 Bad Gateway"

- A 502 from the proxy often indicates a timeout. The OpenAI/Claude request may be taking longer than the proxy’s allowed execution time.
- **Solution:** Increase your AWS Lambda function timeout. We recommend at least **120 seconds** (and 180+ seconds if using very large models like GPT-5).
- If using API Gateway for the proxy, consider switching to a Lambda Function URL, which supports longer running times for responses.

### Network Errors (e.g. connection failed)

- Check your internet connection if you’re using cloud AI providers.
- Verify that the Proxy URL is correct and that your proxy service is running/accessible.
- For local models: confirm that LM Studio is running on your machine and listening on the expected URL (default is `http://localhost:1234` for LM Studio).

### Settings Not Saving

- Ensure that Unity has permission to write to your project (the **Assets/** folder especially). If you're using source control, make sure the files in `Assets/Editor/UnityAgent/` are not locked or read-only.
- After entering settings, you can force a save by going to **File > Save Project** in Unity.
- Verify that the settings asset exists: `Assets/Editor/UnityAgent/Settings/AIAssistantSettings.asset`. (If not, re-import the plugin to regenerate it.)

## Configuration

### Model Settings

You can adjust default AI settings in the configuration asset or via the UI:

- Open the file **Assets/Editor/UnityAgent/Settings/AIAssistantSettings.asset** in Unity (select it in the Project window).
- Here you can set the **Default Model** (e.g., choose GPT-4 vs GPT-3.5 as the default) and parameters like **Temperature** (controls how creative or deterministic the AI’s responses are) and **Max Tokens**.
- Alternatively, these options can be configured through the AI Assistant **Settings** window (click the ⚙ button and look for model settings).

### Conversation History Settings

The `AIAssistantSettings.asset` also allows you to tweak how conversation history is managed:

- **Max Conversations** – the number of past conversations to keep saved (default is 50).
- **Max History Messages** – how many recent messages from the conversation to include as context for the AI (default is 20). This essentially controls the context length the AI receives from the history.
- **Auto-Save** – whether conversations are automatically saved (enabled by default).

### Context Detail Level

You can choose how much of your project’s code context to include with each AI prompt. This is configured in the AI Assistant Settings (or via the UI dropdown if provided):

- **Minimal** – Only a high-level project summary (fastest and uses the fewest tokens).
- **Summary** – Project structure and class/method outlines.
- **Standard** – Summaries of relevant files (balanced detail; recommended for most use-cases).
- **Full** – The complete contents of relevant files (most detailed, but uses more tokens).

Selecting a lower context level can save tokens and cost, while higher levels provide the AI with more information for potentially better answers. Choose the level that makes sense for your query.

## Security Notes

- Your API keys are stored **locally** in the project at `Assets/Editor/UnityAgent/.api_keys.json`. (This file is automatically added to **.gitignore** to prevent accidental commits.)
- **Never commit your API keys** or share them publicly. Treat them like passwords.
- All API usage is billed to your own accounts (OpenAI, Anthropic, etc.). There are no additional charges from this plugin itself. Monitor your usage on those platforms to avoid unexpected costs.

## Limitations

- **Editor-Only:** UnityAgent runs in the Unity Editor environment. It does *not* work in runtime builds of your game.
- **Internet Required (for Cloud):** If you’re using OpenAI or Anthropic, you need an internet connection to reach those services. (Local LLM mode can work offline once you have a model on your machine.)
- **Proxy Required (for Cloud):** A proxy server is needed for OpenAI/Claude API usage due to Unity Editor limitations (not required for local models).
- **File Scope:** In Agent Mode, the AI can only create or modify files within your Unity project's `Assets/` directory. It won't touch files outside of your project or perform operations outside the Unity Asset folder.

## Support

If you encounter issues or have questions, try the following:

1. Re-read the **Troubleshooting** section above to see if your issue is covered.
2. Review the proxy setup guides (`Proxy/PROXY_SETUP_GUIDE.md` and `Proxy/LAMBDA_TESTING_GUIDE.md`) if you are having proxy or connection issues.
3. Verify that you meet the **Requirements** (especially Unity version 6.x or above, and proper setup of keys/proxy).
4. If the problem persists, consider searching the GitHub issues or opening a new issue for help.

## License

This plugin is released as-is, without warranties. Use it responsibly. Remember that when using any third-party AI service, you must adhere to that provider’s terms of service and you are responsible for any fees incurred by your usage.

---

**Note:** UnityAgent acts as a bridge between the Unity Editor and external AI services. All AI processing happens on the servers of the model providers (OpenAI, Anthropic, or your local server). **No data is sent to Unity or any other party by this plugin** – your AI queries go directly to the provider you choose, and any costs are billed by that provider to your account. Enjoy the flexibility and control as you build with AI assistance!