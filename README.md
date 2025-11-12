# Wizarr API Client

A Python application for creating Wizarr invitations in batches with various configuration options. This tool interacts with the Wizarr API to automate the creation of invitation links.

## Features

- **Batch Creation**: Create multiple invitations at once
- **Flexible Configuration**: Support for all API options including:
  - Server IDs
  - Expiration dates (1, 7, or 30 days)
  - Access duration (limited or unlimited)
  - Library access permissions
  - Download permissions
  - Live TV access
  - Mobile upload permissions
- **JSON Configuration**: Use configuration files for complex setups
- **Error Handling**: Robust error handling with retry logic
- **Progress Tracking**: Real-time progress output

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or if using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Basic Usage

Create a single invitation:

```bash
python wizarr_client.py --api-key YOUR_API_KEY --count 1 --server-ids 1
```

### Batch Creation

Create multiple invitations:

```bash
python wizarr_client.py --api-key YOUR_API_KEY --count 10 --server-ids 1 2
```

### Advanced Options

Create invitations with specific permissions:

```bash
python wizarr_client.py \
  --api-key YOUR_API_KEY \
  --count 5 \
  --server-ids 1 2 \
  --expires-in-days 7 \
  --duration 30 \
  --library-ids 1 2 3 \
  --allow-downloads \
  --allow-live-tv \
  --allow-mobile-uploads
```

### Using Configuration Files

Create a JSON configuration file (`config.json`):

```json
{
  "count": 10,
  "server_ids": [1, 2],
  "expires_in_days": 7,
  "duration": "unlimited",
  "unlimited": true,
  "library_ids": [1, 2, 3],
  "allow_downloads": true,
  "allow_live_tv": false,
  "allow_mobile_uploads": false
}
```

Then run:

```bash
python wizarr_client.py --api-key YOUR_API_KEY --config config.json
```

### Command-Line Options

#### Required Options
- `--api-key`: Your Wizarr API key (required)

#### Batch Options
- `--count`: Number of invitations to create (required if `--config` not used)
- `--config`: Path to JSON configuration file
- `--stop-on-error`: Stop batch creation on first error

#### Invitation Parameters
- `--server-ids`: Array of server IDs (space-separated, required)
- `--expires-in-days`: Days until invitation expires (1, 7, or 30)
- `--duration`: User access duration in days or "unlimited" (default: "unlimited")
- `--no-unlimited`: Disable unlimited user access
- `--library-ids`: Array of library IDs to grant access to (space-separated)
- `--allow-downloads`: Allow user downloads
- `--allow-live-tv`: Allow live TV access
- `--allow-mobile-uploads`: Allow mobile uploads

#### API Configuration
- `--base-url`: Base URL of the Wizarr API (default: https://invite.rarbg.zip)

#### Output Options
- `--output`: Output file path for results (JSON format)
- `--quiet`: Suppress progress output

## API Reference

Based on the [Wizarr API documentation](https://invite.rarbg.zip/api/docs/), the following parameters are supported:

### Required Parameters
- `server_ids` (array of integers): Array of server IDs

### Optional Parameters
- `expires_in_days` (integer): Days until invitation expires. Valid values: 1, 7, 30, or null
- `duration` (string): User access duration in days or "unlimited" (default: "unlimited")
- `unlimited` (boolean): Whether user access is unlimited (default: true)
- `library_ids` (array of integers): Array of library IDs to grant access to
- `allow_downloads` (boolean): Allow user downloads (default: false)
- `allow_live_tv` (boolean): Allow live TV access (default: false)
- `allow_mobile_uploads` (boolean): Allow mobile uploads (default: false)

## Examples

### Example 1: Create 5 basic invitations

```bash
python wizarr_client.py --api-key YOUR_API_KEY --count 5 --server-ids 1
```

### Example 2: Create invitations with 7-day expiration

```bash
python wizarr_client.py \
  --api-key YOUR_API_KEY \
  --count 10 \
  --server-ids 1 2 \
  --expires-in-days 7
```

### Example 3: Create invitations with specific library access

```bash
python wizarr_client.py \
  --api-key YOUR_API_KEY \
  --count 3 \
  --server-ids 1 \
  --library-ids 1 2 3 4 \
  --allow-downloads
```

### Example 4: Save results to file

```bash
python wizarr_client.py \
  --api-key YOUR_API_KEY \
  --count 20 \
  --server-ids 1 \
  --output results.json
```

### Example 5: Using configuration file

Create `batch_config.json`:

```json
{
  "count": 15,
  "server_ids": [1, 2, 3],
  "expires_in_days": 30,
  "duration": "unlimited",
  "unlimited": true,
  "library_ids": [1, 2],
  "allow_downloads": true,
  "allow_live_tv": true,
  "allow_mobile_uploads": false
}
```

Run:

```bash
python wizarr_client.py --api-key YOUR_API_KEY --config batch_config.json --output results.json
```

## Output Format

The tool outputs JSON with the following structure:

```json
{
  "results": [
    {
      "success": true,
      "index": 1,
      "data": {
        "message": "Invitation created successfully",
        "invitation": {
          // Invitation details from API
        }
      }
    }
  ],
  "errors": [
    {
      "success": false,
      "index": 2,
      "error": "Error message"
    }
  ],
  "total": 10,
  "successful": 9,
  "failed": 1
}
```

## Error Handling

The client includes automatic retry logic for transient errors (429, 500, 502, 503, 504). If an error occurs:

- The error is logged to stderr
- The error is included in the output JSON
- The batch continues unless `--stop-on-error` is specified
- The exit code will be 1 if any invitations failed

## Programmatic Usage

You can also use the `WizarrClient` class in your own Python code:

```python
from wizarr_client import WizarrClient

# Initialize client
client = WizarrClient(
    base_url="https://invite.rarbg.zip",
    api_key="YOUR_API_KEY"
)

# Create a single invitation
result = client.create_invitation(
    server_ids=[1, 2],
    expires_in_days=7,
    allow_downloads=True
)

# Create multiple invitations
batch_result = client.create_invitations_batch(
    count=10,
    server_ids=[1, 2],
    expires_in_days=7,
    allow_downloads=True
)
```

## License

This project is provided as-is for use with the Wizarr API.

## API Documentation

For the complete API documentation, visit: https://invite.rarbg.zip/api/docs/
