from pathlib import Path

from htag_data_pipeline.endpoints import ENDPOINTS


DEFAULT_PIPELINE_CONFIG_PATH = Path(__file__).with_name("pipeline_config.yml")
PIPELINE_STEPS = ("ingest", "clean", "upload")


def _parse_scalar(value):
    value = value.strip()
    if not value:
        return ""
    if value[0] == value[-1] and value.startswith(("'", '"')):
        return value[1:-1]
    return value


def _parse_pipeline_config_yaml(text):
    """Parse the small YAML subset used by pipeline_config.yml."""
    config = {"pipelines": {}}
    section = None
    current_pipeline = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            if section != "pipelines":
                raise ValueError(f"Unsupported top-level config section '{section}' on line {line_number}")
            continue

        if section != "pipelines":
            raise ValueError(f"Expected 'pipelines:' before line {line_number}")

        if indent == 2 and stripped.endswith(":"):
            current_pipeline = stripped[:-1]
            config["pipelines"][current_pipeline] = {}
            continue

        if indent == 4 and current_pipeline and ":" in stripped:
            key, value = stripped.split(":", 1)
            config["pipelines"][current_pipeline][key.strip()] = _parse_scalar(value)
            continue

        raise ValueError(f"Unsupported pipeline config syntax on line {line_number}: {raw_line}")

    return config


def load_pipeline_config(config_path=None):
    """Load YAML pipeline switches from disk."""
    path = Path(config_path) if config_path else DEFAULT_PIPELINE_CONFIG_PATH
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        config = _parse_pipeline_config_yaml(text)
    else:
        config = yaml.safe_load(text)

    validate_pipeline_config(config, config_path=path)
    return config


def validate_pipeline_config(config, config_path=None):
    if not isinstance(config, dict):
        raise ValueError(f"Pipeline config must be a mapping: {config_path}")

    pipelines = config.get("pipelines")
    if not isinstance(pipelines, dict):
        raise ValueError(f"Pipeline config must contain a 'pipelines' mapping: {config_path}")

    for pipeline_name, pipeline_config in pipelines.items():
        if not isinstance(pipeline_config, dict):
            raise ValueError(f"Pipeline '{pipeline_name}' must be a mapping")

        for step in PIPELINE_STEPS:
            choice = pipeline_config.get(step)
            if choice not in {"Y", "N"}:
                raise ValueError(
                    f"Pipeline '{pipeline_name}' step '{step}' must be 'Y' or 'N'; got {choice!r}"
                )


def pipeline_step_enabled(config, pipeline_name, step, default=False):
    pipeline_config = config.get("pipelines", {}).get(pipeline_name, {})
    choice = pipeline_config.get(step)
    if choice is None:
        return default
    return choice == "Y"


def endpoint_step_enabled(config, endpoint, step, default=True):
    endpoint_path = endpoint.get("path") if isinstance(endpoint, dict) else endpoint
    for pipeline_config in config.get("pipelines", {}).values():
        if pipeline_config.get("path") == endpoint_path:
            return pipeline_config.get(step) == "Y"
    return default


def enabled_endpoints_for_step(config, step, endpoints=None):
    configured_endpoints = endpoints or ENDPOINTS
    return [
        endpoint
        for endpoint in configured_endpoints
        if endpoint_step_enabled(config, endpoint, step, default=True)
    ]
