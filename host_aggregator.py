#!/usr/bin/env python3
"""
Host Aggregator Script

This script fetches host files from multiple sources and aggregates them into a
single CSV dataset.
Each run creates a new dataset with a timestamp.
"""

import argparse
import csv
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Set

import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Host sources configuration
HOST_SOURCES = {
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts": (
        "Adware & Malware"
    ),
    (
        "https://raw.githubusercontent.com/StevenBlack/hosts/master/"
        "alternates/fakenews-only/hosts"
    ): "Fake news",
    (
        "https://raw.githubusercontent.com/StevenBlack/hosts/master/"
        "alternates/gambling-only/hosts"
    ): "Gambling",
    (
        "https://raw.githubusercontent.com/StevenBlack/hosts/master/"
        "alternates/porn-only/hosts"
    ): "Porn",
    (
        "https://raw.githubusercontent.com/StevenBlack/hosts/master/"
        "alternates/social-only/hosts"
    ): "Social",
}

# CSV headers
CSV_HEADERS = [
    "entry",
    "category",
]


def fetch_host_file(url: str) -> str:
    """
    Fetch host file content from URL.

    Args:
        url: URL to fetch the host file from

    Returns:
        Raw content of the host file

    Raises:
        requests.RequestException: If the request fails
    """
    try:
        logger.info(f"Fetching host file from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        raise


def should_filter_entry(hostname: str) -> bool:
    """
    Check if a hostname should be filtered out (localhost, loopback, system entries).
    
    Args:
        hostname: The hostname to check
        
    Returns:
        True if the entry should be filtered out, False otherwise
    """
    # Convert to lowercase for case-insensitive comparison
    hostname_lower = hostname.lower()
    
    # List of hostnames to filter out
    filtered_hostnames = {
        'localhost',
        'localhost.localdomain', 
        'local',
        'broadcasthost',
        'ip6-localhost',
        'ip6-loopback',
        'ip6-localnet',
        'ip6-mcastprefix',
        'ip6-allnodes',
        'ip6-allrouters',
        'ip6-allhosts',
        '0.0.0.0'
    }
    
    return hostname_lower in filtered_hostnames


def parse_host_file(content: str, category: str) -> List[Dict[str, str]]:
    """
    Parse host file content and extract host entries.

    Args:
        content: Raw content of the host file
        category: Category for the host entries

    Returns:
        List of dictionaries containing host entry data
    """
    entries = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Parse host entry (format: IP hostname [hostname2 ...])
        # We're looking for lines that start with 0.0.0.0 or 127.0.0.1
        match = re.match(r"^(0\.0\.0\.0|127\.0\.0\.1)\s+(.+)$", line)
        if match:
            hostnames = match.group(2).split()

            # Extract each hostname as a separate entry
            for hostname in hostnames:
                # Clean up hostname (remove any trailing comments)
                hostname = hostname.split("#")[0].strip()
                if hostname and not hostname.startswith("#"):
                    # Filter out localhost and system entries
                    if should_filter_entry(hostname):
                        logger.debug(f"Filtered out system entry: {hostname}")
                        continue
                    
                    entry = {
                        "entry": hostname,
                        "category": category,
                    }
                    entries.append(entry)

    logger.info(f"Parsed {len(entries)} entries from {category}")
    return entries


def deduplicate_entries(entries: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Remove duplicate entries, keeping the first occurrence.

    Args:
        entries: List of host entry dictionaries

    Returns:
        Deduplicated list of entries
    """
    seen = set()
    unique_entries = []

    for entry in entries:
        hostname = entry["entry"]
        if hostname not in seen:
            seen.add(hostname)
            unique_entries.append(entry)
        else:
            logger.debug(f"Duplicate entry found: {hostname}")

    logger.info(
        f"Removed {len(entries) - len(unique_entries)} duplicate entries"
    )
    return unique_entries


def write_csv(entries: List[Dict[str, str]], output_path: str) -> None:
    """
    Write entries to CSV file.

    Args:
        entries: List of host entry dictionaries
        output_path: Path to write the CSV file
    """
    try:
        # Only create directory if output_path has a directory component
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(entries)

        logger.info(
            f"Successfully wrote {len(entries)} entries to {output_path}"
        )
    except Exception as e:
        logger.error(f"Failed to write CSV file: {e}")
        raise


def generate_output_filename() -> str:
    """
    Generate output filename with timestamp.

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"host_entries_{timestamp}.csv"


def main():
    """
    Main function to orchestrate the host aggregation process.
    """
    logger.info("Starting host aggregation process")

    all_entries = []

    # Fetch and parse each host source
    for url, category in HOST_SOURCES.items():
        try:
            content = fetch_host_file(url)
            entries = parse_host_file(content, category)
            all_entries.extend(entries)
        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
            continue

    if not all_entries:
        logger.error("No entries were processed. Exiting.")
        return

    # Deduplicate entries
    unique_entries = deduplicate_entries(all_entries)

    # Generate output filename
    output_filename = generate_output_filename()

    # Always write to data directory
    output_path = f"data/{output_filename}"

    # Write CSV file
    write_csv(unique_entries, output_path)

    # Also write a latest.csv file for easy access
    latest_path = output_path.replace(output_filename, "latest.csv")
    write_csv(unique_entries, latest_path)

    logger.info("Host aggregation completed successfully!")
    logger.info(f"Total entries processed: {len(all_entries)}")
    logger.info(f"Unique entries: {len(unique_entries)}")
    logger.info(f"Output files: {output_path}, {latest_path}")


if __name__ == "__main__":
    main()
