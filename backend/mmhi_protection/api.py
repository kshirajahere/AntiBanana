from .mmhi_pipeline import MMHIPipeline

_api_instance = None

def get_mmhi_api(default_strength="medium"):
    global _api_instance
    if _api_instance is None:
        _api_instance = MMHIPipeline()
    return _api_instance
