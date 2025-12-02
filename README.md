# Host DNI Host Aggregator

A GitHub CI/CD pipeline that runs daily to aggregate host entries from multiple sources into a single CSV dataset. This tool fetches host files from StevenBlack's hosts repository and creates structured datasets for blocking malicious domains.

## Features

- **Daily Automation**: Runs automatically every day at 2:00 AM UTC via GitHub Actions
- **Multiple Sources**: Aggregates from 5 different host file categories
- **CSV Output**: Creates structured CSV files with standardized columns
- **Deduplication**: Removes duplicate entries across sources
- **Easy-to-Access URLs**: CSV files are deployed to GitHub Pages for simple, memorable URLs
- **Artifact Storage**: Each run creates a timestamped dataset stored as GitHub Actions artifacts
- **Latest Alias**: Always maintains a `latest` artifact that points to the most recent CSV
- **Automatic Cleanup**: Artifacts are automatically purged after a configurable retention period (default: 30 days)

## Host Sources

The aggregator fetches from these sources:

| Source | Category | Description |
|--------|----------|-------------|
| [Adware & Malware](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) | Adware & Malware | Main hosts file |
| [Fake News](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-only/hosts) | Fake news | Fake news domains |
| [Gambling](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-only/hosts) | Gambling | Gambling-related domains |
| [Porn](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn-only/hosts) | Porn | Adult content domains |
| [Social](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/social-only/hosts) | Social | Social media domains |

## CSV Schema

The generated CSV files contain the following columns:

| Column | Description | Example Values |
|--------|-------------|----------------|
| `entry` | The hostname/domain | `example.com`, `ads.example.com` |
| `category` | Source category | `Adware & Malware`, `Fake news`, `Porn`, `Social`, `Gambling` |
| `action` | Action type | `block` (default) |
| `description` | Human-readable description | `Blocked adware & malware domain` |
| `risk` | Risk level | `` (blank by default) |
| `is_enabled` | Whether entry is active | `True` (default) |

## Setup

### Prerequisites

- Python 3.11 or higher
- Git
- GitHub repository

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd hostdni-host-aggregator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run linting tools** (optional):
   ```bash
   # Format code with black
   black host_aggregator.py test_aggregator.py
   
   # Organize imports with isort
   isort host_aggregator.py test_aggregator.py
   
   # Check code quality with flake8
   flake8 host_aggregator.py test_aggregator.py
   ```

4. **Run the script locally**:
   ```bash
   python host_aggregator.py
   ```

5. **Check output**:
   - `host_entries_YYYYMMDD_HHMMSS.csv` - Timestamped dataset
   - `latest.csv` - Latest dataset (overwritten each run)

### GitHub Actions Setup

1. **Push to GitHub**: The workflow is already configured and will run automatically.

2. **Manual Trigger**: You can manually trigger the workflow from the GitHub Actions tab.

3. **Enable GitHub Pages** (Recommended):
   - Go to repository **Settings** → **Pages**
   - Under "Source", select the `gh-pages` branch
   - Click **Save**
   - After the first workflow run, your CSV files will be available at:
     - `https://<username>.github.io/<repo>/artifacts/latest.csv`
     - `https://<username>.github.io/<repo>/artifacts/host_entries_YYYYMMDD_HHMMSS.csv`

4. **Access Data**: Generated CSV files are available in two ways:
   - **GitHub Pages** (Recommended): Simple, memorable URLs that don't change
   - **GitHub Actions Artifacts**: Navigate to the workflow run and download artifacts

## Usage

### Accessing the Latest Dataset

The latest aggregated dataset is available via **GitHub Pages** (recommended) or **GitHub Actions artifacts**:

#### GitHub Pages (Recommended - Easy-to-Remember URLs)

Once GitHub Pages is enabled, your CSV files are accessible at stable URLs:

**Latest CSV:**
```
https://hostdni.github.io/host-aggregator/artifacts/latest.csv
```

**Timestamped CSV:**
```
https://hostdni.github.io/host-aggregator/artifacts/host_entries_YYYYMMDD_HHMMSS.csv
```

These URLs are permanent and easy to remember - perfect for programmatic access, sharing, or integration into other systems.

**Direct Download Example:**
```bash
# Download latest CSV directly
curl -O https://hostdni.github.io/host-aggregator/artifacts/latest.csv

# Or use in Python
import pandas as pd
df = pd.read_csv('https://hostdni.github.io/host-aggregator/artifacts/latest.csv')
```

#### GitHub Actions Artifacts (Alternative)

**Via GitHub UI:**
1. Go to the [Actions tab](https://github.com/<username>/<repo>/actions) in your repository
2. Click on the most recent workflow run
3. Scroll down to the **Artifacts** section
4. Download the `latest` artifact

**Note**: Artifact URLs change with each workflow run and require authentication for programmatic access.

### Programmatic Access

**Using GitHub API:**
```python
import requests
import pandas as pd
from io import StringIO

# GitHub API endpoint to list artifacts
owner = "<username>"
repo = "<repo-name>"
token = "<your-github-token>"  # Optional, but recommended for rate limits

# Get the latest workflow run
headers = {"Authorization": f"token {token}"} if token else {}
runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
runs_response = requests.get(runs_url, headers=headers)
runs_data = runs_response.json()

# Get the most recent successful run
latest_run = next(
    (run for run in runs_data["workflow_runs"] if run["status"] == "completed"),
    None
)

if latest_run:
    # Get artifacts for this run
    artifacts_url = latest_run["artifacts_url"]
    artifacts_response = requests.get(artifacts_url, headers=headers)
    artifacts_data = artifacts_response.json()
    
    # Find the 'latest' artifact
    latest_artifact = next(
        (a for a in artifacts_data["artifacts"] if a["name"] == "latest"),
        None
    )
    
    if latest_artifact:
        # Download the artifact
        download_url = latest_artifact["archive_download_url"]
        download_response = requests.get(download_url, headers=headers)
        
        # Extract and load CSV (artifacts are zipped)
        import zipfile
        from io import BytesIO
        
        with zipfile.ZipFile(BytesIO(download_response.content)) as z:
            with z.open("latest.csv") as f:
                df = pd.read_csv(f)
        
        # Filter by category
        adware_domains = df[df['category'] == 'Adware & Malware']['entry'].tolist()
        
        # Get all entries
        all_domains = df['entry'].tolist()
```

**Note**: For easier programmatic access, use the GitHub Pages URLs (see above) which don't require authentication and provide stable, memorable URLs.

### Using with Host Files

You can use the CSV data to generate custom host files:

```python
import pandas as pd

# Load dataset
df = pd.read_csv('latest.csv')

# Generate host file format
host_entries = []
for _, row in df.iterrows():
    if row['action'] == 'block' and row['is_enabled'] == 'True':
        host_entries.append(f"0.0.0.0 {row['entry']}")

# Write to file
with open('custom_hosts.txt', 'w') as f:
    f.write('\n'.join(host_entries))
```

## Workflow Details

### Schedule

- **Frequency**: Daily at 2:00 AM UTC
- **Manual Trigger**: Available via GitHub Actions UI
- **Timezone**: UTC (configurable in workflow file)

### Process Flow

1. **Fetch**: Downloads host files from all configured sources
2. **Parse**: Extracts hostnames from each file
3. **Deduplicate**: Removes duplicate entries
4. **Generate**: Creates timestamped CSV file
5. **Upload Artifacts**: Uploads timestamped CSV and `latest.csv` as GitHub Actions artifacts
6. **Deploy to GitHub Pages**: Deploys CSV files to `gh-pages` branch for easy access
7. **Auto-Cleanup**: GitHub automatically purges artifacts after retention period (GitHub Pages files persist)

### Output Files

CSV files are available in two locations:

**GitHub Pages** (Recommended - Permanent URLs):
- **`artifacts/latest.csv`** - Always points to the most recent CSV
  - URL: `https://hostdni.github.io/host-aggregator/artifacts/latest.csv`
- **`artifacts/host_entries_YYYYMMDD_HHMMSS.csv`** - Timestamped CSV files
  - URL: `https://hostdni.github.io/host-aggregator/artifacts/host_entries_YYYYMMDD_HHMMSS.csv`

**GitHub Actions Artifacts** (Alternative - Auto-purged after retention period):
- **`latest`** - Artifact alias that always points to the most recent CSV
- **`host_entries_YYYYMMDD_HHMMSS.csv`** - Timestamped artifact

### Storage Management

The system automatically manages storage by:
- **GitHub Pages**: CSV files are deployed to the `gh-pages` branch and persist until the next update
- **Retention Policy**: Artifacts are kept for a configurable period (default: 30 days, max: 90 days)
- **Automatic Cleanup**: GitHub automatically purges artifacts after the retention period expires
- **Latest Alias**: The `latest` artifact and `latest.csv` on GitHub Pages always point to the most recent CSV
- **Repository Size**: Main branch stays clean; only `gh-pages` branch contains CSV files
- **Artifact Limits**: GitHub provides generous artifact storage (10 GB for free tier)

## Customization

### Adding New Sources

Edit `host_aggregator.py` and add new entries to `HOST_SOURCES`:

```python
HOST_SOURCES = {
    "https://example.com/hosts": "Custom Category",
    # ... existing sources
}
```

### Modifying CSV Schema

Update the `CSV_HEADERS` list and modify the entry creation logic:

```python
CSV_HEADERS = ['entry', 'category', 'action', 'description', 'risk', 'is_enabled', 'custom_field']
```

### Changing Schedule

Modify the cron expression in `.github/workflows/daily-aggregation.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2:00 AM UTC
```

### Modifying Retention Period

Change the retention period by modifying the `ARTIFACT_RETENTION_DAYS` environment variable in `.github/workflows/daily-aggregation.yml`:

```yaml
env:
  # Artifact retention period in days (1-90 days, GitHub default is 90)
  ARTIFACT_RETENTION_DAYS: 30  # Change this value (1-90)
```

**Note**: The retention period can be set between 1 and 90 days. Artifacts older than this period will be automatically purged by GitHub.

## Monitoring

### GitHub Actions

- Check the Actions tab for run history
- View logs for any failures
- Monitor execution time and success rates

### Data Quality

- Review generated CSV files for completeness
- Check for unexpected duplicates
- Verify category assignments

## Troubleshooting

### Common Issues

1. **Network Timeouts**: Increase timeout in `fetch_host_file()`
2. **Parsing Errors**: Check host file format changes
3. **Artifact Upload Failures**: Check GitHub Actions storage limits and permissions
4. **Artifact Not Found**: Verify the workflow run completed successfully and artifacts were uploaded
5. **GitHub Pages Not Working**: 
   - Ensure GitHub Pages is enabled in repository Settings → Pages
   - Verify the source is set to `gh-pages` branch
   - Check that the workflow has `contents: write` permission
   - Wait a few minutes after the first deployment for GitHub Pages to build

### Debug Mode

Enable debug logging by modifying the script:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Code Quality

This project uses several tools to maintain code quality:

### Linting Tools

- **Black**: Code formatter for consistent Python style
- **isort**: Import organizer for clean import statements  
- **flake8**: Linter for code quality and style enforcement

### Running Linting Tools

```bash
# Format all Python files
black host_aggregator.py test_aggregator.py

# Organize imports
isort host_aggregator.py test_aggregator.py

# Check code quality
flake8 host_aggregator.py test_aggregator.py
```

**Or use the Makefile for convenience:**
```bash
# Format and lint
make check

# Just format
make format

# Just lint
make lint

# Run tests
make test
```

### Pre-commit Setup (Optional)

You can set up pre-commit hooks to automatically run linting:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting tools: `black`, `isort`, `flake8`
5. Test locally
6. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the Actions logs for CI/CD problems
- Review the troubleshooting section above
