# Competitive Intelligence Agent with Amazon Bedrock AgentCore

An automated competitive intelligence gathering system built on Amazon Bedrock AgentCore SDK, featuring browser automation with Chrome DevTools Protocol (CDP), LLM-powered analysis, and comprehensive session recording.

## Architecture Overview

This agent leverages the Amazon Bedrock AgentCore SDK to provide enterprise-grade browser automation and analysis capabilities:

- **Browser Automation**: Managed browser instances with full session recording to S3
- **CDP Integration**: Chrome DevTools Protocol for advanced browser control and network analysis
- **LLM Analysis**: Claude 3.5 Sonnet for intelligent content extraction
- **Code Interpreter**: Sandboxed Python environment for data analysis and visualization
- **LangGraph Orchestration**: State-managed workflow for multi-competitor analysis

## Key Features

### Browser Automation with BedrockAgentCore SDK

#### Managed Browser Sessions
- Creates isolated browser instances using `BrowserClient` from the SDK
- Automatic session management with configurable timeouts
- WebSocket-based connection via CDP for real-time control

#### Session Recording
- Full browser session recording to S3
- Recordings include all navigation, scrolling, and interactions
- Replay capability for compliance and review

#### Live Viewer
- Real-time browser viewing through Amazon DCV technology
- Take/release control functionality for manual intervention
- Multiple display resolutions (720p, 900p, 1080p, 1440p)

### Chrome DevTools Protocol (CDP) Features

#### Network Analysis
```python
# Automatically discovers and tracks API endpoints
- Intercepts network requests in real-time
- Filters ad networks and analytics
- Identifies pricing/feature API calls
```

#### Performance Metrics
```python
# Captures browser performance data
- Page load times
- Resource timing
- Memory usage statistics
```

#### Intelligent Page Discovery
```python
# Automated content discovery through scrolling
- Identifies pricing sections, feature lists, tables
- Smooth scrolling with content detection
- Screenshots at key discovery points
```

### LLM-Powered Extraction

#### Pricing Analysis
- Extracts pricing tiers, plans, and features
- Identifies billing cycles and discounts
- Handles complex pricing structures

#### Feature Extraction
- Core functionality identification
- Technical specification extraction
- Integration and compatibility analysis

### Code Interpreter Integration

The agent uses BedrockAgentCore's Code Interpreter for:
- Data visualization generation
- Comparison matrix creation
- Statistical analysis
- Report generation

## Installation

### Prerequisites

1. **AWS Account** with access to:
   - Amazon Bedrock (Claude 3.5 Sonnet model)
   - Amazon Bedrock AgentCore
   - S3 for recording storage
   - IAM role with appropriate permissions

2. **Python 3.10+**

3. **Required Python packages**:
```bash
pip install -r requirements.txt
```

### Required IAM Permissions

Create an IAM role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock-agentcore:*",
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
```

### Environment Variables

```bash
export AWS_REGION=us-west-2
export AWS_ACCOUNT_ID=your-account-id
export RECORDING_ROLE_ARN=arn:aws:iam::${AWS_ACCOUNT_ID}:role/BedrockAgentCoreRole
export S3_RECORDING_BUCKET=bedrock-agentcore-recordings-${AWS_ACCOUNT_ID}
export S3_RECORDING_PREFIX=competitive_intel/
```

## Usage

### Basic Execution

```bash
cd competitive-intelligence-agent
python run_agent.py
```

### Available Options

When you run the agent, you'll see three options:

```
Select analysis option:
1. 🎯 AWS Bedrock AgentCore Pricing Only
2. 🆚 Compare Bedrock AgentCore vs Vertex AI
3. ✏️  Custom competitors
```

### Example: Analyzing AWS Bedrock AgentCore

```python
# Option 1 will analyze:
{
    "name": "AWS Bedrock AgentCore",
    "url": "https://aws.amazon.com/bedrock/agentcore/pricing/",
    "analyze": ["pricing", "features", "models", "regions"]
}
```

### Example: Custom Competitor Analysis

```python
# Option 3 allows custom input:
competitors = [
    {
        "name": "Stripe",
        "url": "https://stripe.com/pricing",
        "analyze": ["pricing", "features", "apis"]
    },
    {
        "name": "Square",
        "url": "https://squareup.com/us/en/pricing",
        "analyze": ["pricing", "features", "fees"]
    }
]
```

## How It Works

### 1. Browser Initialization
```python
# Creates managed browser with recording
browser_tools.create_browser_with_recording()

# Initializes CDP session for advanced control
cdp_session = await context.new_cdp_session(page)
await cdp_session.send("Network.enable")
await cdp_session.send("Performance.enable")
```

### 2. Intelligent Navigation
```python
# Navigates to target URL
await browser_tools.navigate_to_url(competitor['url'])

# Discovers page content through scrolling
discovered_sections = await browser_tools.intelligent_scroll_and_discover()

# Attempts to find pricing page
found_pricing = await browser_tools.smart_navigation("pricing")
```

### 3. Content Extraction
```python
# LLM-powered extraction with token limit protection
pricing_result = await browser_tools.extract_pricing_info()
features_result = await browser_tools.extract_product_features()
```

### 4. Analysis & Reporting
```python
# Code Interpreter generates visualizations
analysis_tools.create_comparison_visualization(competitor_data)

# Generates final report
analysis_tools.generate_final_report(all_data, analysis_results)
```

## Session Recording & Replay

### Automatic Recording
All browser sessions are automatically recorded to S3:
```
s3://your-bucket/competitive_intel/SESSION_ID/
├── metadata.json
├── batch-001.ndjson.gz
├── batch-002.ndjson.gz
└── ...
```

### Viewing Recordings
After analysis completes, you'll be prompted to view the session replay:
```
View session replay? [Y/n]:
```

The replay viewer allows you to:
- Watch the entire browser session
- See all navigation and scrolling
- Review what was extracted
- Share with stakeholders

## Output Files

The agent generates:

### 1. Analysis Reports
- `reports/competitive_intelligence_report.md` - Comprehensive comparison report
- `analysis/comparison_matrix.csv` - Feature/pricing comparison matrix

### 2. Visualizations
- `visualizations/competitive_analysis_dashboard.png` - Visual comparison charts

### 3. Raw Data
- `analysis/{competitor}_raw_data.json` - Complete extracted data
- `analysis/{competitor}_pricing.txt` - Pricing information
- `analysis/{competitor}_features.txt` - Feature lists

## Advanced Features

### Manual Control During Automation
While the browser is running, you can:
1. Open the live viewer URL shown in console
2. Click "Take Control" to pause automation
3. Manually navigate or interact
4. Click "Release Control" to resume automation

### CDP Network Interception
The agent tracks all API calls made by websites:
```python
# Discovered APIs are logged:
🔍 Found API: https://api.example.com/pricing/v2/plans
🔍 Found API: https://api.example.com/features/list
```

### Performance Monitoring
Captures detailed performance metrics:
```python
{
    "TaskDuration": 2.543,
    "JSHeapUsedSize": 15234567,
    "Documents": 1,
    "Nodes": 1250
}
```

## Troubleshooting

### Common Issues

#### 1. Token Limit Errors
- **Symptom**: "Input is too long for requested model"
- **Solution**: Content is automatically truncated to 10k characters

#### 2. Browser Connection Issues
- **Symptom**: "Target page, context or browser has been closed"
- **Solution**: Agent automatically attempts reconnection

#### 3. Rate Limiting
- **Symptom**: "ThrottlingException"
- **Solution**: Agent implements automatic retry with backoff

#### 4. Recording Playback Issues
- **Symptom**: No events in replay
- **Solution**: Wait 30 seconds after completion for S3 upload

### Debug Mode
Enable detailed logging:
```python
# In config.py
debug_mode = True
```

## Architecture Components

### BedrockAgentCore SDK Usage

#### BrowserClient
- Manages browser lifecycle
- Handles WebSocket connections
- Provides control/release functionality

#### Code Interpreter
- Sandboxed Python execution
- File system access for data processing
- Visualization generation

#### Control Plane API
- Browser creation and configuration
- Recording setup
- Network configuration

### LangGraph Workflow

The agent uses a state machine with the following nodes:
1. `analyze_competitor` - Extracts data from each competitor
2. `process_data` - Aggregates and processes all data
3. `generate_report` - Creates final analysis report

## Limitations

- **Token Limits**: Large pages are truncated to fit LLM context windows
- **Dynamic Content**: Some JavaScript-heavy sites may require longer wait times
- **File Generation**: Code Interpreter files are sandboxed and not directly accessible
- **Recording Size**: Large sessions may take time to upload to S3

## Best Practices

1. **Start Small**: Test with single competitor first
2. **Monitor Live View**: Watch the browser to understand extraction process
3. **Use Manual Control**: Take control if automation gets stuck
4. **Review Recordings**: Use replay for debugging and validation
5. **Check API Discovery**: Review discovered endpoints for additional insights

## Example Output

```
✅ Analysis Complete!
📊 Competitors analyzed: 2
📸 Screenshots taken: 6
🔍 APIs discovered: 52
📄 Report: reports/competitive_intelligence_report.md
📹 Recording: s3://bedrock-agentcore-recordings-xxx/competitive_intel/SESSION_ID/
```

## Support

For issues related to:
- **BedrockAgentCore SDK**: Check AWS documentation
- **Browser automation**: Review Playwright documentation
- **LLM errors**: Verify Bedrock model access
- **S3 permissions**: Check IAM role configuration