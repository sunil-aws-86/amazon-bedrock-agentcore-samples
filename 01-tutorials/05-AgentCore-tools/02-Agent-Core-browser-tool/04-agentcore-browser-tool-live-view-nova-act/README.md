# Live Browser Viewe with Nova Act Integration

Real-time browser viewing and AI automation using AWS Bedrock AgentCore Browser tool with Nova Act.

## Features

- **Live Browser Streaming**: Real-time display via Amazon DCV
- **AI Browser Control**: Natural language automation with Nova Act
- **Configurable Display**: Multiple viewport sizes (720p, 900p, 1080p, 1440p)
- **Interactive Control**: Take/release browser control functionality

## Prerequisites

- AWS account with Bedrock AgentCore Browser access
- Nova Act API key from [nova.amazon.com](https://nova.amazon.com)
- Required packages: `bedrock-agentcore`, `nova-act`, `rich`
- Amazon DCV SDK files

## Setup

1. Install dependencies:

```bash
pip install bedrock-agentcore nova-act rich
```

2. Configure credentials:

```python
NOVA_ACT_API_KEY = "your_api_key_here"
```

3. Set AWS credentials (temporary or permanent)

## Usage

```bash
python live_view_nova_act.py
```

The script will:

1. Create AWS browser session in us-west-2
2. Start live viewer server on port 8008
3. Open browser automatically
4. Execute Nova Act automation (Amazon coffee maker search)
5. Display results while maintaining live view

## Controls

- **Ctrl+C**: Stop the application
- **Browser UI**: Take/release control, resize display
- **Live View**: Real-time browser interaction display

## Configuration

- **Region**: Change `us-west-2` in browser_session()
- **Port**: Modify `port=8008` in BrowserViewerServer()
- **Display Size**: Default 1600×900, configurable via UI
- **Starting Page**: Modify `starting_page` in NovaAct()
