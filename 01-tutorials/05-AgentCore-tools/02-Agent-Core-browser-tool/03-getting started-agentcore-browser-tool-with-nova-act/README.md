# Browser Automation with Nova Act

This script demonstrates automated web browsing using Amazon Bedrock AgentCore's browser client integrated with Nova Act for AI-powered web interactions.

## Overview

The script automates the process of:

1. Initializing a browser session through Amazon Bedrock AgentCore
2. Connecting to Nova Act's AI-powered browser automation service
3. Performing automated web actions (searching for products on Amazon)
4. Extracting and returning structured data from web pages

## Prerequisites

### Required Dependencies

```bash
pip install bedrock-agentcore nova-act rich
```

### API Keys

- **Nova Act API Key**: Required for AI-powered browser automation
  - Replace `NOVA_ACT_API_KEY = "xxxx"` with your actual API key
  - Obtain from https://nova.amazon.com/act

### AWS Configuration

- AWS credentials configured for `us-west-2` region
- Access to Amazon Bedrock AgentCore browser services

## Code Structure

### Main Components

#### Browser Session Initialization

```python
with browser_session("us-west-2") as client:
```

- Creates a managed browser session in AWS us-west-2 region
- Automatically handles browser lifecycle and cleanup

#### Nova Act Integration

```python
with NovaAct(
    cdp_endpoint_url=ws_url,
    cdp_headers=headers,
    preview={"playwright_actuation": True},
    nova_act_api_key=NOVA_ACT_API_KEY,
    starting_page="https://www.amazon.com",
) as nova_act:
```

- Connects to browser via Chrome DevTools Protocol (CDP)
- Enables Playwright actuation for enhanced browser control
- Sets Amazon.com as the starting page

#### AI-Powered Action Execution

```python
result = nova_act.act(
    "Search for a coffee maker and extract the details of the first result."
)
```

- Executes natural language instructions on the web page
- Returns structured data based on the requested action

## Usage

### Basic Execution

```bash
python basic_browser_nova_act.py
```

### Expected Workflow

1. **Initialization Phase** (20 seconds)

   - Browser session starts
   - WebSocket connection established
   - Nova Act service connects

2. **Navigation Phase**

   - Automatically navigates to Amazon.com
   - Page loads and becomes ready for interaction

3. **Action Phase**

   - Executes search for "coffee maker"
   - Identifies first search result
   - Extracts product details

4. **Result Phase**
   - Returns structured data about the found product
   - Displays results in console

## Configuration Options

### Customizable Parameters

| Parameter                      | Description                     | Default                    |
| ------------------------------ | ------------------------------- | -------------------------- |
| `starting_page`                | Initial URL to load             | `"https://www.amazon.com"` |
| `region`                       | AWS region for browser session  | `"us-west-2"`              |
| `preview.playwright_actuation` | Enable enhanced browser control | `True`                     |

### Modifying Search Behavior

To change the search action, modify the instruction string:

```python
result = nova_act.act("Your custom instruction here")
```

## Error Handling

The script includes comprehensive error handling:

- **NovaAct Connection Errors**: Catches API key or connection issues
- **Browser Session Errors**: Handles AWS browser service failures
- **General Exceptions**: Provides fallback error reporting

## Output Format

The script returns structured data containing:

- Product information extracted from the search
- Metadata about the automation process
- Error details if any issues occur

## Troubleshooting

### Common Issues

1. **Invalid API Key**

   ```
   NovaAct error: Authentication failed
   ```

   - Verify your Nova Act API key is correct

2. **AWS Credentials**

   ```
   Error in Nova Act execution: AWS credentials not found
   ```

   - Configure AWS CLI or environment variables

3. **Browser Timeout**
   ```
   Browser ready! (but connection fails)
   ```
   - Increase initialization wait time if needed

## Security Notes

- Store API keys securely (use environment variables in production)
- Ensure AWS credentials follow least-privilege principle
- Monitor browser session usage for cost optimization
