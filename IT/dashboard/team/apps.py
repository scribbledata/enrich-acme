from enrichsdk.app.utils import EnrichAppConfig

class TeamConfig(EnrichAppConfig):
    name = 'team'
    verbose_name = "Team Performance"
    description = f"JIRA analysis and others"
    status = "alpha"
    enable = True
    filename = __file__
    multiple = False
    composition = True
