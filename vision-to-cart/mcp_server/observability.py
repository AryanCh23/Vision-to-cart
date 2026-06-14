import time
from typing import Dict, Any

# Global metrics cache
_metrics: Dict[str, Any] = {
    "requests_received": 0,
    "pipelines_completed": 0,
    "pipeline_errors": 0,
    "start_time": time.time()
}

def record_metric(metric_name: str, value: int = 1):
    """Increments a recorded metric."""
    if metric_name in _metrics:
        _metrics[metric_name] += value
    else:
        _metrics[metric_name] = value
    print(f"[METRIC] {metric_name} incremented by {value}. Current total: {_metrics[metric_name]}")

def get_metrics() -> Dict[str, Any]:
    """Returns the accumulated system metrics."""
    uptime = time.time() - _metrics["start_time"]
    metrics_summary = _metrics.copy()
    metrics_summary["uptime_seconds"] = round(uptime, 2)
    return metrics_summary
