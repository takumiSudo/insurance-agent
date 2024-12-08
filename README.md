# Agentic Project for controlling manual insurance claim tasks

## Overview
This project implements a policy-driven framework for controlling and managing AI agent behaviors in automated tasks. It provides a flexible policy enforcement system that allows you to define and control what actions an AI agent can perform, similar to IAM policies.

## Features
- Policy-based access control for AI agents
- Support for Allow/Deny effects on actions
- Granular control over browser and AI operations
- Conditional policy enforcement
- JSON-based policy definitions

## Getting Started

### Prerequisites
- Python 3.x
- Chrome/Chromium browser (for Selenium-based operations)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic.git
cd agentic
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your configuration:
```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure
```
agentic/
├── policy/
│   ├── policy_enforcer.py  # Core policy enforcement logic
│   └── policy_types.py     # Policy-related type definitions
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── README.md
```

## Usage
The policy enforcer allows you to control AI agent actions through policy statements. Here's a basic example:

```python
from policy.policy_enforcer import PolicyEnforcer
from policy.policy_types import Policy, Statement, Effect, Action

# Create a policy
policy = Policy(
    version="1.0",
    statements=[
        Statement(
            sid="AllowBrowsing",
            effect=Effect.ALLOW,
            actions=[Action.NAVIGATE, Action.READ_PAGE],
            resources=["*"]
        )
    ]
)

# Initialize the enforcer
enforcer = PolicyEnforcer(policy)
```

## Dependencies
- selenium (≥4.15.2) - For browser automation
- webdriver-manager (≥4.0.1) - WebDriver management
- pytest (≥7.4.3) - Testing framework
- openai (≥1.3.0) - OpenAI API integration
- python-dotenv (≥1.0.0) - Environment variable management

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Last Updated
2024-12-09
