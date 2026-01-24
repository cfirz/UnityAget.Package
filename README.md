# AI Editor Agent

A powerful AI assistant integrated directly into the Unity Editor to help you write code, answer questions, and generate ideas without leaving Unity.

<img width="2528" height="1696" alt="card" src="https://github.com/user-attachments/assets/cc3cf363-ad5d-4b4b-8834-9307de472a3d" />

## Features

- **Integrated Chat Interface**: Chat with AI directly inside Unity Editor
- **Agent Mode**:
  - **Code Editing**: Intelligently edit existing scripts with full context
  - **File Management**: Create, delete, and modify files automatically
  - **Scene Operations**: Create and modify GameObjects, add components, and create assets (Materials)
    - **Robust targeting**: Works with inactive objects and supports full hierarchy paths (e.g., `Parent/Child/ObjectName`) to disambiguate names
    - **Active scene preference**: Resolves names in the active scene before other loaded scenes to avoid collisions
    - **Interactive resolution**: If an object isn’t found, the agent can suggest candidates from the scene and ask you to confirm the correct one
    - **Persistence**: Scene modifications mark the scene dirty so changes persist after save/reload
    - **Apply materials**: Apply an existing Material asset to a GameObject’s Renderer via `apply_material`
      - Supports multi-material renderers via optional `material_index` (0-based). If omitted, applies to all slots.
      - Materials can be resolved by `material_path`, `material_name`, or derived names from the GameObject (e.g., `NameMaterial`, `Name_Material`, `Name`).
- **Multi-Step Execution**: Plan and execute complex tasks with multiple steps
  - **Manual confirmation**: Review plan + approve generated changes before applying them
  - **Auto confirmation**: Auto-approve and execute plans for faster iteration
  - **Optimized planning**: Large tasks are bundled into fewer external steps (up to 10), and each step can include multiple internal actions
  - **Internal progress**: When a step contains multiple actions, the output shows per-action progress (e.g., `Internal step i/N: ...`)
  - **Domain reload resilience**: Execution can resume after Unity recompiles scripts / reloads the domain
  - **Retry resilience**: Timeouts are classified for retry backoff, and scene operations allow an extra retry attempt before stopping
- **Context Awareness**:
  - **Project Knowledge Base**: Automatically scans and understands your project structure
  - **Smart Context**: Includes relevant files, console logs, and selected objects in the prompt
  - **Semantic Search**: (Coming soon) Find relevant code by meaning
- **Multi-Provider Support**:
  - **OpenAI**: Support for GPT-5 family, GPT-4.1 family, GPT-4o family, and o-series reasoning models (o1/o3)
  - **Anthropic**: Support for Claude Sonnet/Opus/Haiku (including Opus 4 / 4.1 IDs)
  - **Local LLMs**: Connect to OpenAI-compatible local servers via LM Studio
- **Developer Experience**:
  - **Markdown Support**: Rich text formatting for clearer explanations
  - **Code Highlighting**: Syntax highlighting for code blocks
  - **Execution Transcripts**: Detailed logs of all AI actions
  - **LLM request/response logging**: Proxy logs request metadata and collected responses for debugging

## Installation

1. Clone or download this repository into your Unity project's `Assets` folder (or install via UPM if packaged).
2. Open Unity Editor.
3. Go to `Window > AI Assistant` to open the window.

**UPM (Git URL) note**: Git-based UPM installs are treated as *immutable* by Unity. Your UPM package must include `.meta` files (including folder metas and `package.json.meta`), otherwise Unity will log errors like `... has no meta file, but it's in an immutable folder. The asset will be ignored.`

## Configuration

### API Keys
1. Click the settings icon (⚙) in the AI Assistant window header.
2. Enter your OpenAI or Anthropic API keys.
3. (Optional) Configure Local LLM settings if using LM Studio.

### Proxy (Optional - AWS Lambda)
If you use the included AWS Lambda proxy (`Assets/Proxy/`):

- **Important**: When updating the plugin, redeploy your Lambda using the latest `Assets/Proxy/lambda_function.py` (OpenAI requests are routed via the **OpenAI Responses API**, and the request/response shaping lives in the Lambda).
- **Setup / testing guides**:
  - `Assets/Proxy/PROXY_SETUP_GUIDE.md`
  - `Assets/Proxy/LAMBDA_TESTING_GUIDE.md`

### Reasoning Controls (Optional)
- **OpenAI o-series**: Set **Reasoning Effort** (low/medium/high) to control reasoning depth.
- **Claude**: Set **Thinking Budget (tokens)** to request extended thinking (0 = use provider default).

### Modes
- **Chat Mode**: Standard conversational interface for Q&A and code generation.
- **Agent Mode**: Autonomous mode that can edit files and perform project operations.
- **Multi-Step Mode**: Planning-based execution for complex tasks.
  - Use the **Auto Confirmation** toggle to switch between **Manual** (off) and **Auto** (on) execution.
  - In **Manual** mode, the plan UI and Pending Changes panel will surface generated file changes so you can **Approve** or **Discard** before execution continues.

## Testing (Contributors)
- **Run StepExecutor tests**: `.\run_tests.ps1 -TestFilter "StepExecutorTests"`
- **Note**: Step execution tests use `IProxyClient` + `MockProxyClient` to avoid real network calls / API keys.

## Agent Mode Capabilities

In Agent Mode, the AI can perform the following actions:

- **Edit Files**: Modify existing scripts (e.g., "Add a jump method to PlayerController.cs")
- **Create Files**: Create new scripts or assets (e.g., "Create a new Enemy script")
- **Delete Files**: Remove obsolete files (e.g., "Delete the old test script")
- **Scene Operations**:
  - **Create GameObjects**: "Create a red Cube at (0, 1, 0)"
  - **Instantiate Prefabs**: "Spawn the Enemy prefab at (5, 0, 5)"
  - **Modify GameObjects**: "Add a Rigidbody to the Player and set its layer to 'Player'"
  - **Manage Objects**: "Delete the 'TempObject' and disable the 'LoadingScreen'"
  - **Create Assets**: "Create a blue material in Assets/Materials"

## Requirements

- Unity 2021.3 or later
- Active internet connection (for cloud models)
- API Key from OpenAI or Anthropic (or local LLM setup)

## License

MIT License
