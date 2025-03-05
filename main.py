"""
Top Daily Docs Add-On
"""

import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta

from documentcloud.addon import AddOn
from documentcloud.toolbox import requests_retry_session


class DailyDocs(AddOn):
    """
    Fetches top viewed docs in the last 24 hours
    and sends and email or Slack alert
    """

    def fetch_graphql_data(self):
        """Runs a graphql query using cURL and retrieves the data"""
        # Get ISO8601 time for 24 hours ago
        start_time = (datetime.utcnow() - timedelta(days=1)).replace(
            microsecond=0
        ).isoformat() + "Z"

        # Load the cURL command from environment variable
        curl_command = os.environ.get("TOKEN")
        if not curl_command:
            raise ValueError("CLOUDFLARE_GRAPHQL_CURL environment variable is not set.")

        # Replace the start time
        curl_command = re.sub(
            r'"\$start":\s*"\$start"', f'"$start": "{start_time}"', curl_command
        )

        # Run the cURL command and capture output
        result = subprocess.run(
            curl_command, shell=True, capture_output=True, text=True, check=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"cURL command failed: {result.stderr}")

        return json.loads(result.stdout)

    def process_data(self, data):
        """
        Processes the data returned from graphql
        and finds the top 5 links
        """
        visit_counts = defaultdict(int)

        for account in data.get("data", {}).get("viewer", {}).get("accounts", []):
            for event in account.get("rumPageloadEventsAdaptiveGroups", []):
                request_path = event["dimensions"].get("requestPath", "Unknown")
                visit_counts[request_path] += event["sum"].get("visits", 0)

        # Sort by total visits and get the top 5
        top_links = sorted(visit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_links_with_base = [
            (f"https://documentcloud.org{path}", visits) for path, visits in top_links
        ]
        return top_links_with_base

    def send_notification(self, subject, message):
        """Send notifications via slack or email"""
        if self.data.get("slack_webhook"):
            requests_retry_session().post(
                self.data.get("slack_webhook"), json={"text": f"{subject}\n\n{message}"}
            )
        else:
            self.send_mail(subject, message)

    def main(self):
        """The main add-on functionality goes here."""
        data = self.fetch_graphql_data()
        top_links = self.process_data(data)

        subject = "Top 5 most viewed documents on DocumentCloud in the last 24 hours:"
        message = ""
        for path, visits in top_links:
            message += f"{path} : {visits} visits\n"
        self.send_notification(subject, message)


if __name__ == "__main__":
    DailyDocs().main()
