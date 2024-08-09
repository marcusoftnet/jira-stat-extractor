# AARO Stats Exporter

We use this script to export data about issues from JIRA to be used in our status reporting. The script creates a CSV file that can be imported into the Google Sheet where the statistical processing happens.

The script gets the issues from the passed in JQL and then parses the changelog for each issue to get the Work Started Status (-s/--workstartedstatus) parameter to get a proper state date

The main reasons for having this script in the first place is that we cannot use "Created" as our start date, since that date often is weeks (and sometime months or years) before actual work starts in the first place. Hence we need to look into the changelog and get the change that indicates the real start of work.

## Using the script

### Prerequisite

The script uses Python 3 and you will have to install that on your computer.

### Quick start

Open a terminal in the same directory as where the `main.py` file is located

Using abbreviations:

```bash
python3 main.py -u {your username} -t {your token} -j {a JQL statement}
```

Using long parameter names:

```bash
python3 main.py --username {your username} --token {your token} --jql {a JQL statement}
```

### Parameters

The script takes 3 required parameters

| Parameter name | Description | Example |
| :--- | :--- | :--- |
| `-u/--username` | The username you have generated a token for. <br/> Typically this is your email address | `-u marcus.hammarberg@aaro.com` |
| `-t/--token` | A token to access the API with. You can [easily generate one here]https://id.atlassian.com/manage-profile/security/api-tokens) | `-t WI34GH9W29843R892F92RH2` |
| `-j/--jql` | A JQl query to get issues for. Note that your user needs to have access to things you are querying for; projects, filters etc. <br/> Supply the JQL statement in **double**quotes. You might need to change the quotes in your query to use single quotes. | `"filter = 'Filter for Team 418' and issuetype=Story and statuscategory=Done"` |

There are also two optional parameters that you only need to supply if the default values are not useful

| Parameter name | Description | Default value | Example |
| :--- | :--- | :--- | :--- |
| `-s/--workstartedstatus` | The name of the status that should start the clock for our work time. Looking up the first time the issue changed into this status, is the main reason for us having to create this script in the first place. <br> The comparison is done case-insensitive. | `Implementing` | `-w Accepted` |
| `-o/--output` | Name and location of the output file. The file will be created if it doesn't exist and overwritten if it does exist. | `jira-stats-export-{date}` | `-o marcus.csv` <br> `-o C:\Users\marcus.hammarberg\Downloads\export.csv` |

## Filters used

For the different teams I have used the following JQL queries:

### Team 418

```text
"filter = 'Filter for Team 418' and issuetype=Story and Resolution=Fixed"
```

### Team 101

```text
"filter = 'Filter for Team 101' and issuetype=Story and Resolution=Fixed"
```

### Team Hakuna Meta Data

```text
"filter = "Filter for Team Hakuna Meta-Data"  and issuetype=Story and Resolution=Fixed"
```

### Team Sudo

```text
"filter = "Filter for Team Sudo"  and issuetype=Story and Resolution=Fixed and key not in (AARO-14406)"
```

