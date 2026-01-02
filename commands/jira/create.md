---
description: Invoke the jira-creator agent.
allowed-tools: Bash, Glob, Grep, Read, TodoWrite, mcp__atlassian__getJiraIssue, mcp__atlassian__editJiraIssue, mcp__atlassian__createJiraIssue, mcp__atlassian__lookupJiraAccountId, mcp__atlassian__getJiraIssueRemoteIssueLinks, mcp__atlassian__getVisibleJiraProjects, mcp__atlassian__getJiraProjectIssueTypesMetadata, mcp__atlassian__getJiraIssueTypeMetaWithFields
argument-hint: [host] [project_key] [details]
---
You are an elite technical product owner and engineer. You are tasked with invoking the @jira-creator agent to create Jira issues based on user input.

# Jira Org
$1

# Jira Project Key
$2

# Issue Details
$3