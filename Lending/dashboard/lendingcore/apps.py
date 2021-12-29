from enrichsdk.app.utils import EnrichAppConfig

class LendingConfig(EnrichAppConfig):
    name = 'lendingcore'
    verbose_name = "Lending Performance"
    description = f"Lending Data Analysis"
    status = "alpha"
    enable = True
    filename = __file__
    multiple = False
    composition = True
