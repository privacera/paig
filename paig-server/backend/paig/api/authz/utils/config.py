from functools import lru_cache

from core.config import load_config_file


@lru_cache
def get_rds_authorizer_cache_timings_config() -> dict | None:
    configs = load_config_file()
    if "authz" in configs or "rds_authorizer" in configs["authz"]:
        if "cache_expiry" in configs["authz"]["rds_authorizer"]:
            return configs["authz"]["rds_authorizer"]["cache_expiry"]


@lru_cache
def get_rds_authorizer_cache_expiry_time(cache_name: str) -> int:
    cache_timings_config = get_rds_authorizer_cache_timings_config()
    if cache_timings_config and cache_name in cache_timings_config:
        return int(cache_timings_config[cache_name])
    else:
        return 60
