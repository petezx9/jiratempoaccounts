from auth import api_token
from jira import JIRA

# Jira server URL
URL = "https://jira.securethingz.com"

# Connect to Jira
jira = JIRA(server=URL, token_auth=api_token)
