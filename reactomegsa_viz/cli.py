import click
import requests
import os
import sys

from .html_report_generator import HtmlReportGenerator

@click.command()
@click.option("--analysis-id", "-a", required=True, help="The ReactomeGSA analysis id.")
@click.option("--html-path", "-p", required=True, help="Target path of the HTML report file. This must not exist.")
@click.option("--reactome-url", "-r", required=False, default="https://gsa.reactome.org", help="Can be used to access a alterantive ReactomeGSA deployments.")
def create_report(analysis_id, html_path, reactome_url) -> None:
    """Downloads the result from ReactomeGSA and creates a HTML report.
    """
    # check if the HTML path exists
    if os.path.exists(html_path):
        print(f"Error: Target HTML path '{html_path}' exists.")
        sys.exit(1)

    # download the ReactomeGSA result
    print("Downloading ReactomeGSA result...")
    requ = requests.get(f"{reactome_url}/0.1/result/{analysis_id}")

    if requ.status_code != 200:
        print(f"Error: Failed to download ReactomeGSA result: {requ.content}")
        sys.exit(1)

    json_result = requ.json()

    # create the HTML file
    HtmlReportGenerator.create_report(json_result, analysis_id, html_path, reactome_url)
    print(f"HTML report written to {html_path}")

if __name__ == "__main__":
    create_report()
