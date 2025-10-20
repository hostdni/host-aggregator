# Host DNI Host Aggregator

A GitHub CI/CD pipeline that runs daily to aggregate host entries from multiple sources into a single CSV dataset. This tool fetches host files from StevenBlack's hosts repository and creates structured datasets for blocking malicious domains.

## Features

- **Daily Automation**: Runs automatically every day at 2:00 AM UTC via GitHub Actions
- **Multiple Sources**: Aggregates from 5 different host file categories
- **CSV Output**: Creates structured CSV files with standardized columns
- **Deduplication**: Removes duplicate entries across sources
- **Version Control**: Each run creates a timestamped dataset
- **Latest File**: Always maintains a `latest.csv` for easy access

## Host Sources

The aggregator fetches from these sources:

| Source | Category | Description |
|--------|----------|-------------|
| [StevenBlack/hosts](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) | Adware & Malware | Main hosts file |
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

3. **Access Data**: Generated CSV files are available in the `data/` directory and can be accessed via:
   ```
   https://raw.githubusercontent.com/<username>/<repo>/main/data/latest.csv
   ```

## Usage

### Accessing the Latest Dataset

The latest aggregated dataset is always available at:
```
https://raw.githubusercontent.com/<username>/<repo>/main/data/latest.csv
```

### Programmatic Access

```python
import pandas as pd
import requests

# Load the latest dataset
url = "https://raw.githubusercontent.com/<username>/<repo>/main/data/latest.csv"
df = pd.read_csv(url)

# Filter by category
adware_domains = df[df['category'] == 'Adware & Malware']['entry'].tolist()

# Get all blocked domains
blocked_domains = df[df['action'] == 'block']['entry'].tolist()
```

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
5. **Update**: Updates `latest.csv` file
6. **Cleanup**: Removes timestamped files older than 30 days
7. **Commit**: Commits changes to repository

### Output Files

- `data/host_entries_YYYYMMDD_HHMMSS.csv` - Timestamped dataset (kept for 30 days)
- `data/latest.csv` - Latest dataset (always current, never deleted)

### Storage Management

The system automatically manages storage by:
- **Retention Policy**: Keeps only the last 30 days of timestamped files
- **Automatic Cleanup**: Removes files older than 30 days during each run
- **Latest File**: Always maintains `latest.csv` regardless of age
- **Repository Size**: Prevents unlimited growth of the repository

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

Change the retention period by modifying the cleanup step in `.github/workflows/daily-aggregation.yml`:

```yaml
- name: Clean up old timestamped files (keep last 30 days)
  run: |
    # Change +30 to desired retention period (in days)
    find data/ -name "host_entries_*.csv" -type f -mtime +30 -delete
```

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
3. **Git Push Failures**: Verify GitHub token permissions

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
