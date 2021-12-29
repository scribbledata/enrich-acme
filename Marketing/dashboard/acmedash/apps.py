from enrichsdk.app.utils import EnrichAppConfig

class MarketingConfig(EnrichAppConfig):
    name = 'acmedash'
    verbose_name = "Marketing Performance"
    description = f"Marketing Data Analysis"
    status = "alpha"
    enable = True
    filename = __file__
    multiple = False
    composition = True
