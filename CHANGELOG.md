# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.26.0] - 2026-01-10

### Added
- **⚠️ Lambda update required (existing proxy users)**: If you use the included AWS Lambda proxy, you must redeploy/update your deployed `Assets/Proxy/lambda_function.py` to this version to keep OpenAI requests working correctly (Responses API routing + request/response shaping).
- **OpenAI Responses API support (proxy + client parsing)**: The included Lambda proxy now routes OpenAI requests via the Responses API, and the Unity client can parse both streaming and non-streaming Responses formats.
- **Expanded model catalog**: Added support for newer OpenAI/Anthropic model IDs (including GPT-5 family, GPT-4.1 family, o3 family, and Claude Opus 4 / 4.1).
- **Model capability shaping**: Requests are now shaped per provider/model (token limit field selection, temperature support, structured output support, and conservative output ceilings).
- **Reasoning controls in Settings**:
  - **Reasoning Effort** for OpenAI o-series models (low/medium/high)
  - **Thinking Budget** (tokens) for Claude extended thinking models
- **Testability improvements**: Added `IProxyClient` + `MockProxyClient` so StepExecutor tests can run without real network calls or API keys.

### Changed
- **Token limit handling**: OpenAI requests prefer `max_output_tokens` (Responses API), and agent-mode output caps are no longer universally clamped to 4096 (now capped per model capability).
- **Settings/model persistence**: Model selection and provider inference are now provider-aware (including Local model round-trip), reducing config drift across reloads.

### Fixed
- **Agent JSON extraction**: Improved `AIAgentParser` JSON extraction so validation produces clearer errors (e.g., missing required fields) and JSON-in-code-block cases parse more reliably.
- **Test runner stability**: Avoids writing API key files / refreshing `AssetDatabase` in test runs; StepExecutor tests avoid deadlocks and hanging by using proper async patterns and mocks.

## [1.25.0] - 2025-12-12

### Added
- **Manual vs Auto Confirmation for Multi-Step**: Multi-step plans can now run in **Manual** mode (explicit approval) or **Auto** mode (auto-approve and execute).
- **Domain Reload Resume for Plans**: Multi-step execution state is persisted so execution can resume after Unity script compilation / domain reloads.
- **Plan UI Improvements**:
  - **Cancel Plan** action added to the plan UI.
  - Clear **“Waiting for user action…”** status surfaced when a plan is awaiting approval / paused.
  - Step list status indicators updated for better readability.

### Changed
- **Multi-Step Behavior**: Plan generation no longer always auto-executes; it now respects the selected confirmation mode (Manual vs Auto).
- **Repo Cleanup**: Removed old loading demo scripts from `Assets/Scripts/`.

### Fixed
- **Manual Approval Deadlock**: Pending changes are surfaced immediately during manual approval so Approve/Discard can reliably unblock execution.
- **Plan Persistence Edge Cases**: Failure/skip progress and selection-only context now persist correctly across reloads; invalid saved state is safely reset.
- **SceneOps Component Errors**: Adding invalid/missing components now returns a clear error instead of silently continuing.

## [1.24.0] - 2025-12-11

### Added
- **Advanced Scene Operations**: Expanded Agent Mode commands for scene management
  - **Instantiate Prefab**: Spawn prefabs while preserving prefab links via `instantiate_prefab`
  - **Delete GameObject**: Remove objects using `delete_gameobject`
  - **Set Active State**: Enable/disable objects using `set_active`
  - **Tag and Layer Support**: Set `tag` and `layer` when creating or modifying GameObjects
- **Schema Enhancements**: Agent JSON schema now includes scene properties (`prefab_path`, `active_state`, `tag`, `layer`)

## [1.23.0] - 2025-12-09

### Added
- **Scene Operations Support**: Agent Mode can now directly manipulate the Unity Scene and create assets
  - **Create GameObjects**: Support for creating primitives (Cube, Sphere, etc.) and empty GameObjects
  - **Modify GameObjects**: Add components and modify properties/fields on existing objects
  - **Create Assets**: Support for creating material assets with shader and color properties
  - **Undo Support**: All scene operations register undo steps for safety
- **New Models Support**: Added support for OpenAI o1 and o3 reasoning models
  - **Model Types**: Support for `o1-preview`, `o1-mini`, and `o3` models
  - **API Compatibility**: Automatic handling of `max_completion_tokens` and parameter restrictions for reasoning models
- **Unity 6000+ Compatibility**: Improved compilation error retrieval
  - Implemented robust reflection-based access to `LogEntries` compatible with Unity 6000+
  - Added fallback mechanisms for error retrieval

### Changed
- **Agent Response Parsing**: Enhanced validation and error handling
  - Improved detection of placeholder text to reject non-functional code responses
  - Better handling of malformed JSON with unescaped newlines in string values
- **Project Operations**: Refactored path handling
  - improved reliability of backup and staging directory paths across platforms
- **UI**: Improved "Apply Changes" button visibility logic in Agent Mode

## [1.22.0] - 2025-12-04

### Added
- **Obfuscation Integration**: Automatic DLL obfuscation in package build pipeline
  - Obfuscar integration for code protection during package builds
  - Automatic Obfuscar detection from multiple installation sources (Chocolatey, NuGet, local tools)
  - Graceful fallback to un-obfuscated DLL if Obfuscar is not available
  - Obfuscated DLLs stored in `Build/Obfuscated/` directory
- **Command-Line Build Support**: Build packages from Unity command line
  - `BuildPackageFromCommandLine.cs` enables batch mode package building
  - `build_package.ps1` PowerShell script for local automated builds
  - Automatic Unity installation detection and compilation validation
  - Comprehensive error reporting and troubleshooting guidance
- **CI/CD Automation**: GitHub Actions workflow for automated package builds
  - Automated package building on push to main/development branches
  - Manual workflow dispatch support
  - Automatic Obfuscar installation in CI environment
  - Build artifacts uploaded for download (packages and obfuscated DLLs)
  - Build logs uploaded for debugging
- **Obfuscar Installation Script**: Automated Obfuscar installation tool
  - `tools/install_obfuscar.ps1` supports multiple installation methods
  - Chocolatey, NuGet, and GitHub direct download installation options
  - Automatic verification of installation success
  - Cross-version compatibility handling for NuGet packages
- **Publishing Guide**: Comprehensive documentation for package publishing
  - Pre-publishing checklist for code quality, documentation, and security
  - Obfuscation setup and configuration instructions
  - Build automation guide for local and CI/CD environments
  - Package structure and validation guidelines

### Changed
- **PackageBuilder**: Enhanced build pipeline with obfuscation support
  - `HandleDll()` now includes obfuscation step before copying to package
  - `PrepareDirectories()` creates `Build/Obfuscated/` directory
  - Build process automatically uses obfuscated DLL when available
  - Improved logging indicates whether obfuscated or raw DLL was used
- **Build Process**: Streamlined package creation workflow
  - Obfuscation integrated seamlessly into existing build pipeline
  - Build continues successfully even if obfuscation fails (uses raw DLL)
  - Enhanced error handling and logging throughout build process
- **Package Structure**: Proxy files now included in package distribution
  - Proxy setup guides and Lambda function code included in package `Proxy/` folder
  - Users can access proxy deployment guides directly from installed package
  - `CopyProxyFiles()` method automatically includes proxy files during build
  - Proxy files moved from root `proxy/` directory to `Assets/Proxy/` for better organization
- **Project Organization**: Improved file structure for packaging
  - Moved proxy files from `proxy/` to `Assets/Proxy/` for inclusion in package builds
  - Moved README.md from `Assets/Editor/UnityAgent/README.md` to `Assets/README.md` for package distribution

### Fixed
- **Project Cleanup**: Removed obsolete files and reorganized structure
  - Moved `SSEParser.cs` from `Assets/Editor/AIAssistant/API/` to `Assets/Demo/` for demo purposes
  - Deleted old execution transcripts from `Assets/Editor/AIAssistant/ExecutionTranscripts/`
  - Cleaned up unused meta files and temporary documentation

## [1.21.0] - 2025-12-04

### Added
- **Plan Generation Status Indicators**: Real-time progress feedback during plan generation
  - Status messages displayed during plan generation: "Analyzing...", "Planning...", "Formatting...", "Arranging..."
  - Status indicators show in conversation window for Chat/Agent modes
  - Status updates integrated into Planning Todo Panel for Multi-Step Mode
  - Loading spinner animation provides visual feedback during plan generation
- **StatusIndicatorUI Component**: Reusable status indicator component for better code organization
  - Extracted status indicator logic from `AIAssistantWindow` into dedicated `StatusIndicatorUI` class
  - Encapsulates streaming box, loading spinner, and text display logic
  - Reduces complexity of main window class (~60 lines moved to component)
  - Reuses existing "streaming box" styling for consistency

### Changed
- **Code Organization**: Refactored status indicator implementation for better maintainability
  - Status indicator logic moved to separate `StatusIndicatorUI` component class
  - `AgentExecutionController.GeneratePlanAsync()` now accepts optional `statusCallback` parameter
  - `StepExecutor` methods updated to support status callbacks during execution
  - Status display logic unified across different execution modes

### Fixed
- **Proxy Cleanup**: Removed unused JavaScript Lambda function implementation
  - Deleted `proxy/lambda_function.js` (Python version is the maintained implementation)
  - Updated proxy documentation to reflect Python-only deployment

## [1.20.0] - 2025-12-04

### Added
- **Smart Context & History Optimization**: Intelligent system for managing conversation context within token limits
  - **Token-Aware History**: Automatically calculates and truncates conversation history to fit within model context windows
  - **Adaptive Summarization**: Automatically summarizes older parts of the conversation when space is running low
  - **Noise Filtering**: Filters out UI status messages (ticks, loading indicators) from the context sent to the AI
- **Semantic Memory Foundation**: Added infrastructure for message embeddings and semantic search integration
- **Design Decision Tracking**: New system to track and retrieve architectural decisions linked to specific files

### Fixed
- **Domain Reload State**: Fixed issue where applying pending changes would sometimes lose state during domain reload
  - Implemented proper state saving before triggering AssetDatabase.refresh
- **Prompt Construction**: Improved "Cursor-style" prompt building for better agent reliability

## [1.19.0] - 2025-12-04

### Changed
- **Project Restructuring**: Major codebase reorganization
  - Renamed main plugin folder from `Assets/Editor/AIAssistant` to `Assets/Editor/UnityAgent`
  - Namespace updated to `UnityAgent.Editor` for better organization
  - Created `UnityAgent.Editor.asmdef` assembly definition for proper dependency management
- **UI Architecture Refactoring**: Improved separation of concerns
  - Moved UI components to `UnityAgent/UI/Components` and `UnityAgent/UI/Controllers`
  - Introduced `AgentExecutionController` and `ResponseHandler` for better logic separation

### Added
- **Packaging System**: New build tools for UPM package generation
  - `PackageBuilder` tool to automate package creation
  - Support for creating `com.cfirz.unityagent` UPM package
  - Placeholder support for DLL obfuscation in build pipeline

## [1.18.0] - 2025-12-03

### Added
- **Staged File Execution**: Multi-step plan execution now stages changes to a temporary directory instead of modifying project files directly
  - **Safety**: Changes are isolated in `Temp/AIAssistant/Staging/` until explicitly applied
  - **Review Workflow**: New "Pending Changes" UI section allows reviewing all staged changes before they affect the project
  - **Atomic Application**: "Apply All" button to commit all staged changes at once
  - **Discard Option**: "Discard All" button to safely clear staged changes without modifying the project
  - **File Comparison**: Comparison window now works with staged files to preview changes before application
- **Step Execution Timeout Monitoring**: Real-time timeout warnings for long-running LLM requests
  - Warnings logged at 30 seconds, then every 60 seconds during request execution
  - Helps identify slow LLM servers or network issues before timeout occurs
  - Background monitoring runs without blocking the main request
- **Request Duration Tracking**: Comprehensive timing information for all API requests
  - Request duration logged on completion and in error handlers
  - Helps identify performance patterns and debug timeout issues

### Changed
- **Step Execution Timeout**: Reduced timeout for step execution from 10 minutes to 3 minutes
  - Step execution requests now use dedicated `HttpClient` with 3-minute timeout
  - Plan generation requests continue using 10-minute timeout for complex operations
  - Faster failure detection when LLM server is slow or unresponsive
- **Execution Workflow**: Multi-step execution no longer validates compilation after each step (since changes are staged, not applied)
  - Compilation validation happens only after applying pending changes
- **Error Handling**: Enhanced timeout and error messages with actionable guidance
  - All timeout errors now include elapsed time and HttpClient timeout value
  - Improved error messages distinguish between different error types (timeout, connection, cancellation)

### Fixed
- **Silent Timeout Failures**: Fixed issue where step execution would hang silently when LLM requests timed out
  - Intermediate timeout warnings now provide visibility into long-running requests
  - Proper error handling ensures timeouts are caught and logged with full context

## [1.17.0] - 2024-12-01

### Added
- **Step Execution Timeout Monitoring**: Real-time timeout warnings for long-running LLM requests
  - Warnings logged at 30 seconds, then every 60 seconds during request execution
  - Helps identify slow LLM servers or network issues before timeout occurs
  - Background monitoring runs without blocking the main request
- **Request Duration Tracking**: Comprehensive timing information for all API requests
  - Request duration logged on completion and in error handlers
  - Helps identify performance patterns and debug timeout issues
  - Duration information included in all timeout error messages

### Changed
- **Step Execution Timeout**: Reduced timeout for step execution from 10 minutes to 3 minutes
  - Step execution requests now use dedicated `HttpClient` with 3-minute timeout
  - Plan generation requests continue using 10-minute timeout for complex operations
  - Faster failure detection for step execution when LLM server is slow or unresponsive
- **Error Handling**: Enhanced timeout and error messages with actionable guidance
  - All timeout errors now include elapsed time and HttpClient timeout value
  - Improved error messages distinguish between different error types (timeout, connection, cancellation)
  - Standardized error message format with consistent troubleshooting guidance
- **StepExecutor Logging**: Enhanced logging throughout step execution lifecycle
  - Detailed logging around request start, completion, and error handling
  - Request duration logged for both successful and failed requests
  - Improved visibility into step execution progress and failures

### Fixed
- **Silent Timeout Failures**: Fixed issue where step execution would hang silently when LLM requests timed out
  - Intermediate timeout warnings now provide visibility into long-running requests
  - Proper error handling ensures timeouts are caught and logged with full context
  - Request duration tracking helps identify patterns in timeout behavior

## [1.16.0] - 2025-11-30

### Added
- **Cursor-Adapted System Prompts**: Centralized prompt system adapted from Cursor IDE (`CursorSystemPrompts.cs`)
  - Defines distinct personas, tool usage guidelines, and code editing protocols
  - **Agent Mode Protocols**: Specialized instructions for code editing, including strict JSON schema enforcement
  - **Response Formatting**: Standardized markdown formatting instructions for consistent output
- **Enhanced Agent Capabilities**: Improved file handling and response reliability
  - **Full File Context**: Agent mode now includes complete file content for editing operations to ensure context awareness
  - **Strict JSON Schema**: Explicit JSON schema validation added to prompts to reduce parsing errors
  - **Step-Specific Prompts**: New `BuildStepExecutionPrompt` for executing plan steps with focused, minimal context
- **Context Awareness Improvements**: Reduced hallucinations and improved relevance
  - **Available Scripts List**: Plan generation prompts now include a list of actual project scripts (from Knowledge Base) to prevent hallucinated file paths
  - **Persistent User Memory**: Automatically includes "User Preferences and Facts" from persistent profile in all prompts
  - **Rules Integration**: Automatically injects custom rules from `Assets/Editor/AIAssistant/Rules/` into the system prompt

### Changed
- **Prompt Construction Refactoring**: Complete rewrite of prompt generation logic
  - Replaced `PromptBuilder` with `MessageBuilder` for asynchronous, context-aware message construction
  - unified "Chat" and "Agent" prompt logic with mode-specific specialized instructions
  - Better handling of conversation history with token-based limiting
- **Model Selection Logic**: Replaced `ModelRecommender` with `ModelSelector`
  - Cross-provider model recommendation (checks both OpenAI and Claude models)
  - Selects best model based on context size requirements vs. available token limits
- **Token Estimation**: Replaced `TokenCalculator` with `TokenEstimator`
  - Centralized token counting and cost estimation logic
  - Updated pricing models for latest GPT-4o and Claude 3.5 Sonnet models
- **Type System**: Centralized core types in `AIAssistantTypes.cs`
  - `ContextBundle` and `Message` types moved to dedicated file for better organization

### Fixed
- **JSON Response Parsing**: Improved `UnescapeContent` method to correctly handle double-escaped characters (newlines, quotes) in agent responses

## [1.15.0] - 2025-01-27

### Added
- **Fixed-Position Streaming Box**: Real-time streaming text display during AI response generation
  - Streaming box appears at fixed position in output window during response generation
  - Height set to 3 lines for consistent display
  - Auto-scrolls to keep streaming box visible during text generation
  - Automatically removed when streaming completes
  - Styled with semi-transparent background for visual distinction
- **Thinking Steps as Assistant Messages**: Thinking steps now integrated directly into conversation flow
  - Thinking steps displayed as assistant messages in the output window
  - Status indicators (⟳ in progress, ✓ completed, ✗ error, • pending) shown in messages
  - Special styling with reduced opacity and italic text to distinguish from final responses
  - Thinking steps preserved in conversation history for context

### Changed
- **Assistant Message Styling**: Removed background color from assistant messages
  - Assistant messages now display without bubble background for cleaner, document-style appearance
  - Maintains consistent spacing and padding for readability
  - User messages retain background color for visual distinction
- **Thinking Panel Repurposed as Todo List**: Thinking panel now displays execution plans
  - Panel title changed from "Thinking Steps" to "Todo list"
  - Displays execution plan steps when available (Multi-Step Mode)
  - Shows progress counter in "To-dos X/Y:" format
  - Expandable/collapsible panel with step status indicators
  - Backward compatible with thinking steps display when no execution plan is present
- **Message Spacing**: Consistent spacing between user and assistant messages
  - Uniform margin-bottom values applied to all message types
  - Even line spacing maintained throughout conversation

### Fixed
- **Streaming Display**: Improved streaming text display with fixed-position box prevents text jumping during generation
- **Message Layout**: Consistent message spacing prevents layout shifts when thinking steps are added

## [1.14.0] - 2025-11-25

### Added
- **Local LM Studio Support**: Connect to local LLM servers running via LM Studio without requiring a proxy server
  - **Local Model Type**: Added "Local" option to model selection dropdown
  - **Local API Provider**: New `APIProvider.Local` provider type for direct local server connections
  - **Local Configuration**: Configurable local server settings stored in `APIKeysConfig`
    - **Local API Base URL**: Default `http://localhost:1234/v1` (configurable)
    - **Local API Key**: Default `lm-studio` (configurable)
    - **Local Model Name**: Free-text field for entering model name as shown in LM Studio (e.g., `deepseek-coder-v2-lite-instruct`)
  - **Direct Connection**: Local requests bypass proxy URL and connect directly to local server
  - **OpenAI-Compatible API**: Uses OpenAI-compatible API format (`/chat/completions` endpoint with `Authorization: Bearer` header)
  - **UI Integration**: Local model name field appears automatically when "Local" model is selected
  - **Settings Window**: Local LLM Configuration section added to API Keys Config Window for easy setup

### Changed
- **ProxyClient**: Enhanced to detect Local provider and route requests directly to local server
  - Local requests use `localApiBase` from `APIKeysConfig` instead of proxy URL
  - Constructs URL as `{localApiBase}/chat/completions` for local requests
  - Uses OpenAI-compatible headers (`Authorization: Bearer`) for local provider
- **ModelConfig**: Updated to handle Local model type
  - `GetModelNameFromEnum()` returns empty string for Local (model name comes from UI field)
  - `GetProviderFromModelType()` returns `APIProvider.Local` for Local model type
- **AIAssistantWindow**: Enhanced model selection UI
  - Shows/hides local model name TextField based on model selection
  - Local model name field persists user input and saves to `APIKeysConfig`
  - Validates local model name is not empty before sending requests
- **APIKeysConfigWindow**: Added Local LLM Configuration section
  - TextField for Local API Base URL with default value and tooltip
  - TextField for Local API Key with default value and tooltip
  - TextField for Local Model Name with tooltip guidance
  - All fields auto-save on change

### Fixed
- **Model Name Handling**: Fixed model name retrieval for Local provider to use UI field value instead of enum conversion

## [1.13.0] - 2025-11-18

### Added
- **Markdown-Based Rich Text Formatting**: LLM messages now display with proper document-style formatting using GitHub-style Markdown
  - **Markdown Parser** (`MarkdownParser.cs`): Converts Markdown text into structured block trees
    - Supports paragraphs, headings (H1-H6), bullet lists, ordered lists, and horizontal rules
    - Handles nested lists with proper indentation tracking
    - Preserves list item continuations (multi-line list items)
    - Integrates seamlessly with existing code block extraction
  - **Markdown Renderer** (`MarkdownRenderer.cs`): Renders Markdown blocks into UI Toolkit VisualElement trees
    - Converts each block type to appropriate VisualElement structure with proper styling
    - Applies USS classes for consistent styling across all Markdown elements
    - Handles spacing, margins, and indentation for proper visual hierarchy
    - Supports nested list rendering with correct layout
  - **Markdown Stylesheet** (`MarkdownStyles.uss`): Comprehensive styling for all Markdown elements
    - Paragraph spacing and margins for readability
    - Heading styles (H1-H6) with progressive font sizes and weights
    - List styles (bullets and numbered) with proper indentation and alignment
    - Horizontal rule styling for visual separators
  - **System Prompt Enhancement**: AI now instructed to format responses in GitHub-style Markdown
    - Uses headings (###) for section titles
    - Uses bulleted lists (-) and numbered lists (1. 2. etc.) for structured content
    - Avoids HTML formatting in favor of Markdown

### Changed
- **Message Display**: Assistant messages now render with full Markdown formatting instead of plain text
  - Replaced `TextField`-based text rendering with `MarkdownRenderer` for structured display
  - Text segments between code blocks are parsed and rendered as Markdown
  - Code blocks remain unchanged and display with syntax highlighting as before
  - Original message content preserved for copy functionality
- **MessageContentParser**: Updated to work with Markdown rendering pipeline
  - `formatText` parameter now defaults to `false` (Markdown rendering replaces TextFormatter)
  - Text segments passed to MarkdownRenderer instead of TextFormatter
  - Maintains backward compatibility with existing code block extraction
- **Streaming Support**: Enhanced streaming message display to support Markdown
  - During streaming, messages display as plain text for immediate feedback
  - After streaming completes, messages are re-rendered with full Markdown parsing
  - Ensures Markdown stylesheet is applied during re-render

### Fixed
- **Message Formatting**: Improved readability of assistant messages with proper document structure
  - Headings now display with appropriate font sizes and spacing
  - Lists display with proper indentation and bullet/number alignment
  - Paragraphs have consistent spacing for better readability

## [1.12.0] - 2025-11-17

### Added
- **Planning Todo Panel**: Expandable todo panel that displays planning steps and progress during plan generation and execution
  - `PlanningTodoPanelUI` component displays execution plan steps as a todo list
  - Shows progress counter in "To-dos X/Y:" format
  - Expandable/collapsible panel with expand button (+/−)
  - Minimized view shows current step description inline with progress
  - Expanded view shows full list of all steps with status indicators
  - Step status indicators: ✓ (completed), ⟳ (in progress), → (current pending), • (pending), ✗ (failed), ⊘ (skipped)
  - Panel positioned at bottom of output container with semi-transparent overlay
  - Automatically shows/hides based on orchestrator state (visible during Planning, AwaitingApproval, Executing, Paused states)
  - Expansion state persists across Unity domain reloads
  - Real-time progress updates during step execution
  - Efficient single-step updates without full panel rebuild
  - Text truncation with tooltips for long step descriptions
  - Custom USS styling via `PlanningTodoPanelStyles.uss`

### Changed
- **AIAssistantWindow**: Integrated planning todo panel into main window
  - Panel created and positioned in `CreateGUI()` method
  - Panel updated when plan is generated via `OnPlanGenerated()` event
  - Panel visibility controlled by `OnOrchestratorStateChanged()` event handler
  - Step progress updated during execution via `OnStepCompleted()` and `ExecutePlanAsync()`
  - Expansion state saved to `_savedPlanningTodoPanelExpanded` field for persistence

## [1.11.0] - 2025-11-16

### Added
- **Auto-Execute Plans**: Multi-step plans now automatically execute without requiring manual approval
  - Plans are generated and immediately executed in Auto mode
  - Planning progress displayed in conversation window: "Planning: Analyzing your request..."
  - Plan summary shown in conversation before execution begins
  - Seamless transition from planning to execution
- **File Change Tracking**: Comprehensive tracking of all file modifications during step execution
  - `FileChangeMetadata` class tracks original content, new content, and change summaries
  - Tracks change types: Created, Modified, Deleted
  - Stores backup paths for revert functionality
  - Associates changes with specific execution steps
- **File Change List UI**: Visual display of all file changes in conversation window
  - `FileChangeListUI` component displays file changes after each step
  - Shows file path, change type badge (NEW/MOD/DEL), and change summary
  - Clickable file paths open comparison window
  - Accept (✓) and Revert (✗) buttons for each file change
  - Reverted files automatically filtered from display
- **File Comparison Window**: Side-by-side comparison view for reviewing changes
  - `FileComparisonWindow` EditorWindow displays original vs modified content
  - Side-by-side layout with line numbers
  - Header shows file path, change type badge, and change summary
  - Footer with Accept, Revert, and Close buttons
  - Handles empty states for created/deleted files
  - Proper UI initialization handling to prevent display issues

### Changed
- **Multi-Step Mode Workflow**: Plans now auto-execute instead of requiring approval step
  - `OnPlanGenerated()` automatically calls `ApprovePlan()` and `ExecutePlanAsync()`
  - Execution mode set to Auto before approval
  - Plan summary displayed in conversation before execution starts
- **Step Execution**: Enhanced to track file changes during execution
  - `StepExecutor.ExecuteStepAttemptAsync()` reads original file content before changes
  - Creates `FileChangeMetadata` objects for each file modification
  - Stores file changes in `StepExecutionResult.FileChanges` list
  - File changes displayed in conversation after each step completes
- **ChatMessage**: Extended to support file change metadata
  - Added `fileChanges` property to `ChatMessage` class
  - File changes serialized with conversation history
  - File change lists displayed when rendering messages
- **ProjectOps**: Added file revert functionality
  - `RevertFileChange()` method restores files from backups
  - Handles Created, Modified, and Deleted file types
  - Deletes created files if no backup exists
  - Returns success/failure status for UI feedback

### Fixed
- **Compilation Error Retrieval**: Improved reliability of Unity LogEntries API access
  - Updated reflection approach to use `System.Type.GetType("UnityEditor.LogEntries,UnityEditor.dll")`
  - Added fallback to assembly-based approach if primary method fails
  - Improved error logging with full stack traces for debugging
  - Per-entry error handling to continue processing even if individual entries fail
  - Enhanced fallback method provides helpful guidance when errors can't be retrieved

## [1.10.0] - 2025-11-16

### Added
- **Hybrid Context-Sharing System**: Intelligent project-aware context system that balances token efficiency with contextual fidelity
  - **Project Knowledge Base**: Persistent knowledge base that parses and caches project structure
    - Automatic project scanning on initialization (limited to 1000 files)
    - Caches class outlines, dependencies, and project summaries to disk
    - Thread-safe singleton pattern with automatic cache invalidation
    - File change detection via `KnowledgeBaseAssetPostprocessor` for automatic updates
    - Cache stored in `Library/AIAssistantCache/knowledge_base.json` for fast loading
  - **Code Parsing**: Regex-based C# code parser extracts project structure
    - Extracts class names, namespaces, base classes, and interfaces
    - Parses method signatures, parameters, and field declarations
    - Builds dependency relationships between classes
    - Generates class descriptions from XML documentation comments
  - **Query Analysis**: Intelligent query analyzer determines relevant code files
    - Extracts explicit file paths from user queries
    - Identifies class names and finds matching files
    - Detects query scope (Broad, Specific, Debug) based on keywords
    - Suggests relevant files based on class relationships and dependencies
    - Event-driven architecture for UI progress updates
  - **Context Retrieval**: Detail-level-based context retrieval system
    - Four detail levels: Minimal, Summary, Standard, Full
    - Minimal: Project summary only (~100 tokens)
    - Summary: Project summary + class outlines (~500 tokens)
    - Standard: Project summary + relevant file summaries (~2000 tokens)
    - Full: Project summary + complete relevant file contents (~8000 tokens)
    - Automatic file limit enforcement (max 10 files) to prevent token overflow
  - **Iterative Refinement Handler**: Detects when LLM requests more context and automatically provides it
    - Pattern matching for context requests ("need more context", "show me the code", etc.)
    - Retrieves additional files based on LLM requests
    - Limits refinement to 5 additional files to control token usage
    - Integrates seamlessly with existing conversation flow
  - **Dependency Graph**: Tracks code dependencies across the project
    - Builds dependency relationships from namespace hierarchies
    - Tracks base classes and interface implementations
    - Provides dependency and dependent lookups for context retrieval
    - Normalized path handling for consistent lookups
  - **Thinking Panel UI**: Visual feedback system showing AI "thinking" steps
    - `ThinkingPanelUI` component displays processing steps in real-time
    - Shows steps like "Analyzing query...", "Found class: X", "Retrieving context..."
    - Status indicators: Pending, InProgress, Completed, Failed
    - Collapsible panel with progress bar and summary statistics
    - Custom USS styling with `ThinkingStepStyles.uss`
  - **Path Utilities**: Centralized path normalization utility
    - `PathUtils.NormalizePath()` ensures consistent path handling
    - Converts absolute paths to relative paths from project root
    - Handles Windows/Unix path separators
    - Used across all context system components
  - **Prompt Size Checking**: Utility for monitoring prompt token usage
    - `PromptSizeChecker` estimates token counts for prompts
    - Helps prevent token limit errors
    - Provides warnings when prompts approach limits
  - **Request Queue**: Queue system for managing API requests
    - Prevents concurrent request conflicts
    - Handles request ordering and cancellation
    - Integrates with rate limit handling

### Changed
- **AIAssistantSettings**: Extended with context system configuration options
  - `contextDetailLevel`: Default context detail level (0-3, default: 2 = Standard)
  - `autoDetectQueryScope`: Enable automatic query scope detection (default: true)
  - `enableSemanticSearch`: Enable semantic search with embeddings (default: false, future feature)
  - `knowledgeBaseAutoRefresh`: Auto-refresh knowledge base on file changes (default: true)
  - `maxProjectSummaryTokens`: Maximum tokens for project summary (default: 500)
- **PromptBuilder**: Enhanced to integrate with context-sharing system
  - `BuildMessages()` now accepts `ContextDetailLevel` parameter
  - Automatically uses `ProjectKnowledgeBase` for project context
  - Integrates `QueryAnalyzer` and `ContextRetriever` for intelligent context selection
  - Includes dependency information for context files
  - Respects detail level settings for token optimization
- **ContextCache**: Extended with knowledge base caching methods
  - `CacheClassOutline()` and `GetCachedClassOutline()` for class outline caching
  - `CacheDependencyGraph()` and `GetCachedDependencyGraph()` for dependency caching
  - Reduces redundant parsing when knowledge base is used
- **ProjectContextProvider**: Enhanced to work with knowledge base system
  - Integrates with `ProjectKnowledgeBase` for richer project summaries
  - Uses cached knowledge base data when available
  - Falls back to basic project info if knowledge base not initialized
- **AIAssistantWindow**: Integrated thinking panel and context system
  - Thinking panel displays during query analysis and context retrieval
  - Automatic knowledge base initialization on window open
  - Context detail level selector in UI
  - Progress indicators for knowledge base operations

### Fixed
- **Path Normalization**: Consistent path handling across all context system components
  - All components now use `PathUtils.NormalizePath()` for consistency
  - Prevents dependency graph lookup failures due to path mismatches
  - Handles both Windows and Unix path separators correctly

## [1.9.0] - 2025-11-16

### Added
- **Multi-Step LLM Execution Flow**: Structured "plan → approve → execute" workflow for complex tasks
  - **Plan Generation**: AI breaks down user tasks into numbered, atomic steps (2-10 steps per plan)
    - Plans generated via structured JSON output from LLM
    - Plan includes step descriptions and context file references
    - Plans validated for structure and step count before approval
  - **Plan Editor UI**: Interactive plan review and editing interface
    - View all steps in an editable list with descriptions
    - Reorder steps using up/down buttons
    - Edit step descriptions inline
    - Delete individual steps
    - Regenerate plan if unsatisfied with initial result
  - **Step Execution**: Sequential execution of plan steps with progress tracking
    - Each step executes with minimal context (only files referenced in step)
    - Step status indicators: Pending, InProgress, Completed, Failed, Skipped
    - Real-time progress updates during execution
    - Automatic retry logic (up to 2 retries) for failed steps
    - Compilation validation after code changes
  - **Execution Controls**: Pause, resume, and cancel execution at any time
    - Pause execution between steps
    - Resume from paused state
    - Cancel execution and return to idle state
  - **Context Caching**: Intelligent file content caching to reduce token usage
    - File content cached with hash-based change detection
    - Cache invalidated when files are modified
    - Reduces redundant file reads and API costs
  - **File Backup System**: Automatic backups before file modifications
    - Backups created in `Backups/` directory with timestamps
    - Backup registry tracks all backups created during execution
    - Restore functionality available for all backed up files
  - **Execution Summary**: Comprehensive summary after plan completion
    - Tracks files created, modified, and deleted
    - Step completion statistics (completed, failed, skipped)
    - Token usage tracking and cost estimation
    - Execution time measurement
  - **Execution Transcripts**: Markdown transcripts saved after execution
    - Complete execution log with step-by-step results
    - Saved to `Assets/Editor/AIAssistant/ExecutionTranscripts/` directory
    - Includes plan details, step results, and summary
  - **Token Usage Tracking**: Per-step and total token usage monitoring
    - Tracks input and output tokens for each step
    - Estimates API costs based on provider pricing
    - Token usage included in execution summary
  - **Integration with Conversation System**: Multi-step plans integrated with existing conversation history
    - Plans and execution results saved as conversation messages
    - Execution history accessible via conversation system
    - Plan context maintained across conversation sessions

### Changed
- **Mode Selection**: Added "MultiStep" mode option alongside "Chat" and "Agent" modes
  - Default mode set to "MultiStep" in `AIConfig.json`
  - Mode toggle in UI switches between Chat, Agent, and MultiStep modes
- **PromptBuilder**: Enhanced with plan-specific prompt building methods
  - `BuildPlanGenerationPrompt()` - Creates prompts for plan generation with structured output instructions
  - `BuildStepExecutionPrompt()` - Creates prompts for executing individual steps with minimal context
  - Plan prompts include JSON schema requirements for structured responses
- **AIAssistantWindow**: Extended with multi-step workflow UI
  - Plan editor panel for viewing and editing execution plans
  - Execution controls (Pause, Resume, Stop buttons)
  - Step status indicators in plan display
  - Execution progress tracking in conversation messages

## [1.8.0] - 2025-01-XX

### Added
- **External Rules Loading**: Users can now add custom rule files to automatically include in AI prompt context
  - Created `Assets/Editor/AIAssistant/Rules/` folder for user-defined rule files
  - Supports `.txt`, `.md`, and `.text` file extensions
  - Files are loaded in alphabetical order and automatically appended to system prompts
  - Rules are loaded fresh on each prompt build, allowing changes without Unity restart
  - Graceful error handling: missing folder or file read errors are logged but don't block functionality
  - Rules are appended after system prompts and project context, before user messages
  - System prompts remain hardcoded in code to prevent breaking response structure

## [1.7.1] - 2025-11-10

### Changed
- **Plugin Folder Organization**: Reorganized AIAssistant plugin folder structure for better maintainability
  - Created logical subfolders: `Core/`, `UI/`, `Styles/`, `API/`, `Agents/`, `Context/`, `Parsing/`, and `Config/`
  - Moved all C# scripts to appropriate folders based on functionality
  - Moved all USS style files to `Styles/` folder
  - Updated hardcoded paths in `AIAssistantWindow.cs` to reference new `Styles/` folder location
  - Improved code organization and navigation within the plugin

## [1.7.0] - 2025-11-10

### Added
- **Assistant Message Text Formatting**: Improved readability of assistant messages with automatic text formatting
  - **Sentence Breaks**: Automatically adds line breaks after sentences (periods) for better readability
    - Intelligently avoids breaking after decimals, URLs, file paths, version numbers, and abbreviations
    - Skips sentence breaks within list items to preserve list formatting
  - **Bullet Point Formatting**: Formats various bullet point styles (`-`, `*`, `•`) with consistent indentation and spacing
    - Normalizes different bullet styles to a consistent format
    - Handles nested bullets with proper indentation
    - Adds proper spacing before and after bullet lists
  - **Numbered List Formatting**: Formats numbered lists (`1)`, `2)`, `1.`, `2.`, etc.) with proper alignment
    - Converts inline numbered items to line-start format for better readability
    - Handles multi-line list items with proper indentation
    - Aligns numbers consistently regardless of digit count
  - **Formatting Preservation**: Original unformatted text is preserved for copy functionality
    - Users can copy the original text without formatting modifications
    - Formatting is applied only to the display, not the stored content
  - **Smart Formatting Rules**: Intelligent detection of edge cases
    - Recognizes common abbreviations (Dr., Mr., etc., i.e., e.g., etc.)
    - Detects URLs and prevents breaking within them
    - Identifies file paths and version numbers to avoid incorrect breaks
    - Handles decimal numbers and prevents breaking within them

### Changed
- **Message Display**: Assistant messages now display with improved formatting for better readability
  - Text formatting is applied automatically to all assistant messages
  - User messages remain unformatted (preserve original input)
  - Formatting works for both streaming and completed messages
- **Code Block Handling**: Text formatting is applied to text segments while preserving code blocks
  - Code blocks remain unformatted (preserve code structure)
  - Text segments between code blocks are formatted for readability
  - Formatting is integrated into the message parsing pipeline

## [1.6.0] - 2025-11-09

### Added
- **Code Block Collapse/Expand**: Code blocks in conversation messages can now be collapsed and expanded
  - Click the arrow (▼/▶) next to the language label to toggle code block visibility
  - Code blocks start expanded by default
  - Arrow indicator changes direction to reflect current state (▼ = expanded, ▶ = collapsed)
  - Improves UI organization when viewing long code snippets

### Fixed
- **JSON Parsing**: Fixed parsing errors when AI generates JSON with literal newlines in string values
  - Added `FixMalformedJson()` method to automatically escape newlines and special characters
  - Handles cases where AI generates JSON with unescaped newlines, tabs, and other control characters
  - Prevents "Invalid JSON" errors when parsing agent mode responses
- **Agent Response Formatting**: Improved display of agent mode responses
  - Comment-only actions now display formatted text instead of raw JSON
  - Agent responses are properly rebuilt after formatting to show readable content
  - Better handling of escaped content in comments and responses

## [1.5.0] - 2025-11-08

### Added
- **Conversation History System**: Continuous chat flow with persistent conversation history
  - `Conversation` and `ChatMessage` classes for managing conversation data
  - `ConversationManager` singleton for save/load/delete operations
  - Conversations automatically saved to `Assets/Editor/AIAssistant/Conversations/` directory
  - Automatic cleanup of old conversations (configurable max count, default: 50)
  - Conversation index file for fast metadata loading
- **Chat-Style UI**: Messaging app-style interface for conversations
  - `MessageBubbleUI` for displaying user and assistant messages in chat bubbles
  - `CodeBlockUI` for syntax-highlighted code blocks within messages
  - `MessageContentParser` for parsing markdown and code blocks in messages
  - Real-time streaming updates in message bubbles
  - Auto-scroll to latest message
- **Conversation History Panel**: History dropdown with advanced features
  - `ConversationUI` component for managing conversation list
  - Search functionality to find conversations by title or message content
  - Date grouping (Today, This Week, This Month, older by month/year)
  - Favorites/star functionality to mark important conversations
  - "New Conversation" button to start fresh conversations
  - Conversation selection to load and continue previous chats
- **Context Integration**: Conversation history automatically included in LLM context
  - `PromptBuilder.BuildMessages()` now accepts `Conversation` parameter
  - Previous messages from conversation included in context (configurable max, default: 20)
  - Conversation history helps AI maintain context across multiple messages
  - User message context (selection, console errors) preserved in conversation history

### Changed
- **AIAssistantWindow**: Major UI overhaul for conversation-based workflow
  - Replaced single output text field with message container showing chat bubbles
  - Added conversation header with title display and history button
  - Integrated conversation loading on window open (loads most recent conversation)
  - Auto-save conversations after each message exchange
  - Conversation title auto-generated from first user message
- **AIAssistantSettings**: Added conversation configuration options
  - `maxConversations`: Maximum number of conversations to keep (default: 50)
  - `maxHistoryMessages`: Maximum previous messages to include in context (default: 20)
  - `autoSaveConversations`: Whether to auto-save conversations (default: true)
- **PromptBuilder**: Enhanced to support conversation history
  - `BuildMessages()` method now accepts optional `Conversation` parameter
  - Automatically includes previous messages from conversation in LLM context
  - Respects `maxHistoryMessages` setting to limit context size
- **Git Ignore**: Added `Assets/Editor/AIAssistant/Conversations/` to exclude conversation files from version control

## [1.4.0] - 2025-11-08

### Added
- **Multi-Provider AI Support**: Full support for both OpenAI and Anthropic Claude AI providers
  - `APIProvider` enum and `ProviderConfig` class for provider abstraction
  - Provider-specific API handling (base URLs, endpoints, authentication headers)
  - Automatic provider detection based on selected model type
  - Support for Claude models: Claude 3 Opus, Claude 3.5 Sonnet, Claude 3 Sonnet, Claude 3 Haiku
  - Default model changed to Claude 3.5 Sonnet (ClaudeSonnet45)
- **Secure API Key Management**: Local storage system for API keys with per-provider support
  - `APIKeysConfig` class for managing API keys stored in `Assets/Editor/AIAssistant/.api_keys.json`
  - Separate API keys for OpenAI and Claude providers
  - Automatic `.gitignore` exclusion to prevent accidental commits
  - `APIKeysConfigWindow` editor window for easy API key configuration
  - Settings button (⚙) in main window to access API key configuration
- **Provider-Specific API Handling**: Intelligent handling of API differences between providers
  - Claude uses `x-api-key` header with `anthropic-version` header
  - OpenAI uses `Authorization: Bearer` header
  - Claude uses `max_tokens` parameter (not `max_completion_tokens`)
  - Automatic parameter selection based on provider and model type
  - Provider routing via `X-Provider` header for proxy compatibility

### Changed
- **Default Model**: Changed default model from GPT-5 to Claude 3.5 Sonnet (ClaudeSonnet45)
- **Model Configuration**: Added `provider` field to `ModelConfig` class
  - Models now include provider information for proper API routing
  - Model selection automatically switches to appropriate provider
- **Request Factory**: Enhanced to handle provider-specific request building
  - Provider-specific parameter handling (max_tokens vs max_completion_tokens)
  - Provider-specific temperature support (Claude supports temperature, GPT-5 doesn't)
  - Provider-specific JSON response format (OpenAI only)
- **Proxy Client**: Enhanced to handle provider-specific authentication
  - Automatic header selection based on provider type
  - Provider information included in request headers for proxy routing
  - Improved error handling for provider-specific API errors

### Fixed
- **API Key Storage**: Fixed API key persistence to use secure local storage
  - Keys stored in `.api_keys.json` (excluded from git)
  - Per-provider key management prevents key conflicts
  - Automatic key loading on window initialization

## [1.3.0] - 2025-11-06

### Added
- **GPT-5 Model Support**: Full support for GPT-5 and newer OpenAI models
  - Automatic detection of GPT-5+ models and use of `max_completion_tokens` instead of `max_tokens`
  - Special handling for GPT-5 temperature restrictions (uses default temperature of 1.0)
  - Support for GPT-4o and GPT-4oMini models
  - Default model changed to GPT-5
- **Lambda Function URL Support**: Enhanced proxy to support both API Gateway and Lambda Function URLs
  - Lambda Function URLs support up to 15 minutes timeout (vs API Gateway's 29 seconds)
  - Automatic event format normalization for seamless compatibility
  - Improved CORS configuration for Function URLs
- **Enhanced Error Handling**: Better detection and handling of Cloudflare blocking and HTML error responses
  - Detects HTML error pages and provides meaningful error messages
  - Improved timeout handling for slower models (GPT-5 requires extended timeouts)
  - Enhanced logging with masked API keys for security
- **Improved Debugging**: Comprehensive request/response logging
  - Full request logging including model, temperature, token limits, and message content
  - Response status and header logging for troubleshooting
  - Request size warnings for large file content requests

### Changed
- **System Prompt**: Simplified and optimized system prompt for better AI responses
  - More concise instructions focusing on Unity and C# best practices
  - Enhanced refactoring guidelines with incremental, safe approach
  - Better emphasis on code completeness and compilation readiness
- **Request Factory**: Enhanced token limit handling
  - Automatic detection of GPT-5+ models requiring `max_completion_tokens`
  - Conditional temperature parameter (omitted for GPT-5 models)
  - Backward compatibility with older models using `max_tokens`
- **Lambda Proxy Timeout**: Extended timeouts for GPT-5 models
  - GPT-5 non-streaming requests: 120 seconds (2 minutes)
  - File content requests: 180 seconds (3 minutes)
  - Streaming requests: 290 seconds (up to API Gateway limit)
  - Default non-streaming: 90 seconds
- **Model Configuration**: Updated default model to GPT-5
  - Added GPT5, GPT4o, GPT4oMini to ModelType enum
  - Reordered enum to prioritize newer models

### Fixed
- **Parameter Compatibility**: Fixed parameter handling for GPT-5 models
  - Correctly uses `max_completion_tokens` for GPT-5+ models instead of `max_tokens`
  - Omits temperature parameter for GPT-5 (which doesn't support custom temperature)
  - Prevents sending incompatible parameters that could cause API errors
- **Lambda Event Handling**: Fixed compatibility issues between API Gateway and Function URL event formats
  - Automatic event normalization ensures both formats work seamlessly
  - Proper header extraction for both event types
- **Error Response Parsing**: Improved handling of HTML error responses from Cloudflare or gateways
  - Detects HTML responses and extracts meaningful error messages
  - Provides specific error messages for 502, 503, and 504 status codes

## [1.2.0] - 2025-01-05

### Changed
- **Agent Mode UI Improvements**: Removed popup confirmation dialog; replaced with "Apply Changes" button positioned next to the output area for better workflow
- **Output Formatting**: Agent Mode now displays formatted, readable code suggestions instead of raw JSON responses
  - Code content is properly unescaped with correct line breaks and formatting
  - Displays action type, file path, comment, and formatted code content in a readable format
- **JSON Parser Enhancements**: Improved JSON extraction to intelligently skip non-JSON code blocks (C#, Python, JavaScript, etc.)
  - Parser now correctly identifies and extracts JSON from markdown code blocks while ignoring code examples
  - Better validation ensures only JSON matching the expected schema is parsed
  - Prevents "No JSON found" errors when responses contain code examples

### Fixed
- **Parsing Errors**: Fixed issue where parser would incorrectly extract C# code blocks as JSON, causing parse failures
- **Apply Button Visibility**: Fixed Apply button not appearing in Agent Mode after successful parsing
- **Response Display**: Fixed Agent Mode showing raw JSON with escaped sequences instead of formatted, readable code
- **Error Handling**: Improved error messages and debug logging for better troubleshooting of parsing issues

## [1.1.0] - 2024-12-28

### Added
- **Agent Mode**: New interactive mode that allows AI to automatically modify Unity project files based on structured JSON responses
  - Supports file operations: create, edit, delete, and comment-only actions
  - Automatic file path detection from user prompts
  - Full file content inclusion for better context when editing files
  - Agent mode toggle in UI with Chat/Agent selection
  - "Apply Change" button for manual application in Chat mode
  - Structured JSON response parsing from AI model
  - File operation logging to `AI_Agent_Log.txt` for audit trail
  - Configuration via `Assets/Editor/AIConfig.json` with mode, autoCommit, and contextLines settings
- **Enhanced Lambda Proxy**:
  - Automatic timeout detection for file content requests (extends to 120 seconds)
  - Improved response validation and error handling
  - Better CloudWatch logging for debugging
  - Enhanced JSON response validation
  - Header validation for API Gateway compatibility
- **Troubleshooting Documentation**:
  - `proxy/TROUBLESHOOTING_502.md` - Comprehensive guide for fixing 502 Bad Gateway errors
  - `proxy/LAMBDA_TESTING_GUIDE.md` - Guide for testing Lambda function directly
  - Test event JSON files for both agent and chat modes

### Changed
- **Prompt Builder**: Enhanced to detect file paths in prompts and automatically include full file content
- **Request Factory**: Increased max_tokens to 4000 when file content is detected in agent mode
- **Proxy Client**: Added support for non-streaming responses required for agent mode JSON parsing
- **Lambda Function**: Major improvements to error handling, timeout management, and response format validation

### Fixed
- **Lambda Timeout Issues**: Fixed 502 Bad Gateway errors caused by Lambda function timeout being too low (3 seconds) for file content requests
  - Lambda now automatically detects file content and uses extended timeout (120 seconds)
  - Added comprehensive troubleshooting guide for timeout configuration
- **Response Validation**: Enhanced validation of Lambda responses to ensure API Gateway compatibility
- **Error Handling**: Improved error messages and logging for better debugging

## [Previous Versions]

_Note: Previous versions were not tracked in this changelog._
