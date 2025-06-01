# Installation

This guide will help you install and set up the DevTrack SDK in your project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A DevTrack account and API credentials

## Installation Steps

1. Install the package using pip:

```bash
pip install devtrack-sdk
```

2. Verify the installation:

```python
import devtrack
print(devtrack.__version__)
```

## Configuration

To use the SDK, you'll need to configure your API credentials. You can do this in two ways:

### Environment Variables

Set the following environment variables:

```bash
export DEVTRACK_API_KEY="your-api-key"
export DEVTRACK_API_SECRET="your-api-secret"
```

### Configuration File

Create a configuration file at `~/.devtrack/config.yaml`:

```yaml
api_key: your-api-key
api_secret: your-api-secret
```

## Next Steps

- Check out the [Quick Start Guide](quickstart.md) to begin using the SDK
- Explore the [API Reference](../api/overview.md) for detailed information
- Learn about [Authentication](../api/authentication.md) methods

## Troubleshooting

If you encounter any issues during installation:

1. Ensure you have the correct Python version installed
2. Verify your pip installation is up to date
3. Check that you have the necessary permissions to install packages
4. Ensure your API credentials are valid

For additional help, please visit our [GitHub repository](https://github.com/yourusername/devtrack-sdk) or contact our support team. 