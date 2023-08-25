# jira-migration
A tool to copy tempo account codes from a jira server to jira cloud.
you can run it multiple times and fix errors as you go.

i'm no Pythonista so be kind and use at your own risk :-).

# VScode devcontainer
## Setting up poetry
After cloning, open  the workspace in vscode and the devcontainer run the poetry install from a terminal
```
poetry install
```
Close VScode and reopen, the poetry environment will automatically be the poetry interpreter vscode uses

> **_NOTE:_** If you have already run poetry install on a windows host the poetry environment will be set up wrong for working inside the container. you will need to removed and install again from the devcontainer terminal


## Using git in the devcontainer
In a devcontainer terminal you may need to set up your git, example running
```
git config  user.name "firstname lastname"
git config  user.email "firstname.lastname@gmail.com"
```
Or in your windows host you can set up *ssh-agent* {google it}, this will forward your SSH key from your host into the devcontainer so it can pass them on to git.

Or you can use https when git cloning.
