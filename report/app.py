import os
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    Response,
    content_types,
)
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.metrics import Metrics, MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from atlassian import Jira
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models import Epic, Sprint, Issue
from constants import (
    issue_status_color,
    issue_status_label,
    sprint_status_color,
    epic_color_map,
)

jira_url = os.getenv("JIRA_URL")
jira_user = os.getenv("JIRA_USER")
jira_password = os.getenv("JIRA_PASSWORD")
jira_board_id = int(os.getenv("JIRA_BOARD_ID", 0))
jira_epic_color_field = "customfield_10017"
jira_issue_sprint_field = "customfield_10020"

app = APIGatewayRestResolver()
logger = Logger()
metrics = Metrics(namespace="Labs")

jira = Jira(jira_url, username=jira_user, password=jira_password)


@app.get("/epic")
def get_epic_details():
    key = app.current_event.get_query_string_value("key", "ISSUE-0")
    epic = get_epic(key)
    child_issues = get_child_issues_for_epic(key)

    todo_count, inprogress_count, done_count = get_issues_stats(child_issues)

    return Response(
        status_code=200,
        content_type=content_types.TEXT_HTML,
        body=render_template(
            "epic-details.html",
            epic=epic,
            issue_status_color=issue_status_color,
            issue_status_label=issue_status_label,
            jira_url=jira_url,
            child_issues=child_issues,
            todo_count=todo_count,
            inprogress_count=inprogress_count,
            done_count=done_count,
        ),
    )


@app.get("/sprint-report")
def get_sprint_report():
    active_sprint = get_active_sprint(jira_board_id)
    issues = get_issues_for_sprint(active_sprint.id)

    todo_count, inprogress_count, done_count = get_issues_stats(issues)

    return Response(
        status_code=200,
        content_type=content_types.TEXT_HTML,
        body=render_template(
            "sprint-report.html",
            sprint=active_sprint,
            issues=issues,
            sprint_status_color=sprint_status_color,
            issue_status_color=issue_status_color,
            issue_status_label=issue_status_label,
            todo_count=todo_count,
            inprogress_count=inprogress_count,
            done_count=done_count,
            jira_url=jira_url,
        ),
    )


def get_issues_stats(issues: list[Issue]) -> tuple[int, int, int]:
    todo_count = len(
        [
            issue
            for issue in issues
            if issue.status == "Prepared" or issue.status == "Backlog"
        ]
    )
    inprogress_count = len(
        [
            issue
            for issue in issues
            if issue.status == "In Progress"
            or issue.status == "Coding Done"
            or issue.status == "In Testing"
        ]
    )
    done_count = len([issue for issue in issues if issue.status == "Done"])
    return todo_count, inprogress_count, done_count


def get_active_sprint(board_id: int) -> Sprint:
    active_sprint = jira.get_all_sprints_from_board(board_id, state="active")
    active_sprint = active_sprint["values"][0]
    sprint = Sprint(
        id=active_sprint["id"],
        name=active_sprint["name"],
        start=active_sprint["startDate"],
        end=active_sprint["endDate"],
        status=active_sprint["state"],
    )
    return sprint


def get_issues_for_sprint(sprint_id: int) -> list[Issue]:
    issues = jira.get_all_issues_for_sprint_in_board(
        jira_board_id, sprint_id, limit=100, fields="key,summary,status,parent,created"
    )
    models = []
    for issue in issues["issues"]:
        epic = (
            get_epic(issue["fields"]["parent"]["key"])
            if "parent" in issue["fields"]
            else None
        )

        models.append(
            Issue(
                key=issue["key"],
                summary=issue["fields"]["summary"],
                created=issue["fields"]["created"],
                status=issue["fields"]["status"]["name"],
                parent=epic,
                sprints=None,
            )
        )

    return models


def get_child_issues_for_epic(epic_key: str) -> list[Issue]:
    issues = jira.jql(
        "'Parent Link' = '{}'".format(epic_key),
        fields="key,summary,status,created,{}".format(jira_issue_sprint_field),
    )
    models = []
    for issue in issues["issues"]:
        sprints = (
            issue["fields"][jira_issue_sprint_field]
            if jira_issue_sprint_field in issue["fields"]
            else None
        )
        sprints = [sprint["name"] for sprint in sprints] if sprints else None
        models.append(
            Issue(
                key=issue["key"],
                summary=issue["fields"]["summary"],
                created=issue["fields"]["created"],
                status=issue["fields"]["status"]["name"],
                parent=None,
                sprints=sprints,
            )
        )

    return models


def get_epic(epic_key: str) -> Epic | None:
    epic_issue = jira.get_issue(
        epic_key,
        fields="summary, description, created, status, {}".format(
            jira_epic_color_field
        ),
        expand="renderedFields",
    )
    if epic_issue:
        epic = Epic(
            key=epic_issue["key"],
            summary=epic_issue["fields"]["summary"],
            created=epic_issue["fields"]["created"],
            status=epic_issue["fields"]["status"]["name"],
            description=epic_issue["renderedFields"]["description"],
            color=epic_color_map(epic_issue["fields"][jira_epic_color_field]),
        )
        return epic


def render_template(template_name: str, **kwargs) -> str:
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(),
    )
    template = env.get_template(template_name)
    return template.render(**kwargs)


@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext):
    metrics.add_metric(name="ReportInvocations", unit=MetricUnit.Count, value=1)
    return app.resolve(event, context)
