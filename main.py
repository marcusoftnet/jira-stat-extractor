import requests
import csv
import sys
import argparse
from requests.auth import HTTPBasicAuth
from datetime import datetime

STATS_CREATOR_NAME = "AARO Stats creator"
STATS_CREATOR_MESSAGE = "Exports a CSV file for the given JQL with the first date each issues enters the status passed in with -s/--workstartedstatus"
AARO_JIRA_API_URL = "https://aarosystems.atlassian.net/rest/api/3"


def load_env(file_path):
    env_vars = {}
    with open(file_path, "r") as file:
        for line in file:
            # Remove leading/trailing whitespace and ignore comments
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def parse_arguments():
    parser = argparse.ArgumentParser(description=STATS_CREATOR_MESSAGE, epilog="")
    parser.add_argument(
        "-u",
        "--username",
        help="Username for your user, typically your AARO email",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--token",
        help="Token for accessing the API. Create one here https://id.atlassian.com/manage-profile/security/api-tokens",
        required=True,
    )
    parser.add_argument(
        "-j",
        "--jql",
        help="The JQL to get issues for",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--workstartedstatus",
        help="The name of the status (case insensitive) that indicate that work has started. We will take look for the first time the status was change for to this. Default is 'Implementing'",
        default="Implementing",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=f"Name of file write the output to. Default is './{generate_file_name()}'. Will overwrite existing files with the same name.",
        default=generate_file_name(),
    )

    return parser.parse_args()

def create_auth(username, token):
    return HTTPBasicAuth(username, token)

def create_request_headers():
    return {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }

def get_resolution_name(issue):
     if issue["fields"]["resolution"] == None:
         return ""
     else:
         return issue["fields"]["resolution"]["name"]

def fetch_issues(args):
    headers = create_request_headers()
    auth = create_auth(args.username, args.token)

    params = {
      "jql": args.jql,
      "maxResults": 1000,
      "fields": "id,key,created,resolutiondate,status,issuetype,resolution",
    }
    url = f"{AARO_JIRA_API_URL}/search"

    response = requests.get(url, headers=headers, auth=auth, params=params)

    if response.status_code == 200:
        issues = response.json()["issues"]
        return [
            {
                "id": issue["id"],
                "key": issue["key"],
                "created": issue["fields"]["created"],
                "resolutiondate": issue["fields"]["resolutiondate"],
                "issuetype": issue["fields"]["issuetype"]["name"],
                "resolution": get_resolution_name(issue),
                "status": issue["fields"]["status"]["name"],
                "statuscategory": issue["fields"]["status"]["statusCategory"]["name"],
            }
            for issue in issues
        ]
    else:
        print(f"Error fetching issues: {response.status_code} {response.text}")
        sys.exit(1)

def fetch_issue_changelog(issue_key, args):
    headers = create_request_headers()
    auth = create_auth(args.username, args.token)
    params = {
        "startAt": 0,
        "maxResults": 1000,
    }

    url = f"{AARO_JIRA_API_URL}/issue/{issue_key}/changelog"
    response = requests.get(url, headers=headers, auth=auth, params=params)

    if response.status_code == 200:
        changelog = response.json()
        return changelog["values"]
    else:
        print(
      f"Error fetching changelog for issue {issue_key}: {response.status_code} {response.text}"
    )
        return []

def find_first_work_started_date(changelog, status_indicating_start):
    for entry in changelog:
        for item in entry["items"]:
            if item["field"] == "status":
                if item["toString"].lower() == status_indicating_start.lower():
                    return entry["created"]
    return None

def generate_file_name():
    return f"jira-stats-export-{datetime.today().strftime('%Y-%m-%d')}.csv"

def convert_date(date_str):
    input_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    output_format = "%Y-%m-%d %H:%M:%S"

    if date_str is None or not date_str:
        return ""

    try:
        date_obj = datetime.strptime(date_str, input_format)
        formatted_date = date_obj.strftime(output_format)
        return formatted_date
    except ValueError:
        return ""

def export_to_csv(issues, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "ID",
                "Key",
                "Created Date",
                "Resolution Date",
                "Issue Type",
                "Status",
                "Resolution",
                "Status Category",
                "Work Started Date",
            ]
        )
        for issue in issues:
            writer.writerow(
                [
                    issue["id"],
                    issue["key"],
                    convert_date(issue["created"]),
                    convert_date(issue["resolutiondate"]),
                    issue["issuetype"],
                    issue["status"],
                    issue["resolution"],
                    issue["statuscategory"],
                    convert_date(issue["work_started_date"]),
                ]
            )

def main():
    print(STATS_CREATOR_NAME)
    args = parse_arguments()
    print("- Arguments parsed")
    print(f"-     User name:           {args.username}")
    print(f"-     JQL:                 {args.jql}")
    print(f"-     Work started state:  {args.workstartedstatus}")
    print(f"-     Output file:         {args.output}")

    # Fetch the issues
    print(f"- Getting issues for '{args.jql}'")
    issues = fetch_issues(args)

    number_of_issues = len(issues)
    print(f"- Got {number_of_issues} issues")

    print(f"- Getting first time each issue entered the '{args.workstartedstatus}' status")
    for i, issue in enumerate(issues):
        print("\r- Getting work-started-date  {}".format(i + 1), end=f"/{number_of_issues}")

        changelog = fetch_issue_changelog(issue["key"], args)
        issue["work_started_date"] = find_first_work_started_date(changelog, args.workstartedstatus)

    # Export the issues to a CSV file
    print(f"\n- Writing result to '{args.output}'")
    export_to_csv(issues, args.output)

if __name__ == "__main__":
    main()
