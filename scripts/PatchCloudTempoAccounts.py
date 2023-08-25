import json
import time

import requests
import atexit

from auth import api_token_cloud_dev, baseUrl, tempoAccessKey, username_cloud_dev
from jiraapi import jira
from requests.auth import HTTPBasicAuth
from tempoapiclient import client_v3


CRED = "\033[91m"
ENDC = "\033[0m"

# you need to get this for your server.
# using a link like this to an issue key in the cloud with a tempo account set can help
# https://<your-jiracloud.com>/rest/api/3/issue/<a jira issue key>
CLOUDTEMPOACCOUNTCUSTOMFIELD = "customfield_10091"  # cloud prod
# CLOUDTEMPOACCOUNTCUSTOMFIELD = "customfield_10154"  # cloud dev


def find_account_id(cound_accounts, account_name):
    """Find new id for tempo account"""
    for A in cound_accounts:
        if A["name"] == account_name:  # type: ignore
            return A["id"]  # type: ignore
    raise Exception(f"account is not found for '{account_name}'")


def update_cloud_issue_tempo_account_id(
    cloud_session: requests.Session,
    issue_key: str,
    new_account_id: int,
    account_name: str,
    failed_issues: list,
):
    """update cloud issue's account filed"""
    # issues url
    url = f"{baseUrl}/rest/api/3/issue/{issue_key}"

    # Query url to get a cloud issues's account
    url_query = f"{url}?fields={CLOUDTEMPOACCOUNTCUSTOMFIELD}"

    response = cloud_session.get(
        url_query,
        headers={"Accept": "application/json"},
    )

    if not response.ok:
        print(
            CRED,
            url_query,
            json.dumps(json.loads(response.text)["errorMessages"]),
            ENDC,
        )
        failed_issues.append(
            f'{url_query} { json.dumps(json.loads(response.text)["errorMessages"]) }'
        )
        return
    old_value = json.dumps(json.loads(response.text)["fields"][CLOUDTEMPOACCOUNTCUSTOMFIELD])

    skip = (old_value != "null") and (json.loads(old_value)["id"] == new_account_id)
    if not skip:
        # update field on cloud issue
        payload = f'{{"fields": {{"{CLOUDTEMPOACCOUNTCUSTOMFIELD}": {new_account_id} }}}}'

        response = cloud_session.put(
            url,
            params={"notifyUsers": "false"},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            data=payload,
        )
        if not response.ok:
            # that did not work so lets print and log details.
            print(
                CRED,
                url_query,
                " Error:",
                response.status_code,
                response.content,
                "  Account ID:",
                new_account_id,
                "  Name:",
                account_name,
                ENDC,
            )
            failed_issues.append(
                f"{url_query} ;{issue_key} ;Error:{response.status_code} {response.content}  ;Account ID: {new_account_id} ;Name:{account_name}"
            )
        else:
            print(f"{url_query}  {issue_key} : {old_value} > {new_account_id}")
    else:
        print(f"{url_query}  {issue_key} : {old_value} > {new_account_id} (SAME SKIPPED)")


def log_failed_issues(failed_issues):
    """Write a log of the failed issues"""
    filename = rf'Failed_Issues{time.strftime("%Y%m%d-%H%M%S")}.txt'
    with open(filename, "w", encoding="utf-8") as fp:
        for i in failed_issues:
            fp.write("%s\n" % i)
        fp.write("END")


def main():
    # Load tempo accounts and there id's form new could server
    tempo = client_v3.Tempo(
        auth_token=tempoAccessKey,  # tempo access key
    )
    cound_accounts = tempo.get_accounts()

    failed_issues = []
    stop = False
    start_at = 0
    max_results = 250
    cloud_session = requests.Session()
    cloud_session.auth = HTTPBasicAuth(username_cloud_dev, api_token_cloud_dev)
    cloud_session.stream = True

    try:
        # We need to do this in blocks as APIis slow and times out
        while not stop:
            # get issues from old jira with an account code,
            issues = jira.search_issues("Account is not EMPTY", start_at, max_results)
            print("start at:", start_at, " Total:", issues.total)  # type: ignore

            for issue in issues:
                issue_key = issue.key  # type: ignore
                # Customfield_12100 is the tempo account field on-prem
                account_name = issue.fields.customfield_12100.name  # type: ignore
                # Get the tempo account id in the cloud this issue is using, by matching the tempo account name from on-prem issue
                new_account_id = find_account_id(cound_accounts, account_name)

                # find issue in cloud by issue key and set tempo account Id
                update_cloud_issue_tempo_account_id(
                    cloud_session, issue_key, new_account_id, account_name, failed_issues
                )
            start_at = start_at + max_results
            stop = start_at >= issues.total  # type: ignore
    except:
        raise
    finally:
        log_failed_issues(failed_issues)

main()
