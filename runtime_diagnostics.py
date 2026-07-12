import gc
import logging
import os
import platform
import sys
import time
import tracemalloc

try:
    import resource
except Exception:
    resource = None


LOGGER = logging.getLogger("pbos.runtime")
if not LOGGER.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def diagnostics_enabled():
    return os.environ.get("PBOS_RUNTIME_DIAGNOSTICS", "").strip().lower() in {"1", "true", "yes", "on"}


def _ensure_tracemalloc():
    if diagnostics_enabled() and not tracemalloc.is_tracing():
        try:
            tracemalloc.start()
        except Exception:
            pass


def get_process_memory_mb():
    try:
        if resource is not None:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            rss = float(getattr(usage, "ru_maxrss", 0.0) or 0.0)
            if sys.platform.startswith("darwin"):
                return rss / (1024.0 * 1024.0)
            return rss / 1024.0
    except Exception:
        return None
    return None


def get_runtime_environment():
    return {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "executable": sys.executable,
        "pid": os.getpid(),
    }


def log_runtime_event(event, **fields):
    if not diagnostics_enabled():
        return
    _ensure_tracemalloc()
    try:
        current, peak = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)
        payload = {
            "event": event,
            "ts": f"{time.time():.3f}",
            "rss_mb": get_process_memory_mb(),
            "traced_current_mb": current / (1024.0 * 1024.0),
            "traced_peak_mb": peak / (1024.0 * 1024.0),
        }
        payload.update(fields)
        LOGGER.info("[RUNTIME] " + " ".join(f"{key}={value}" for key, value in payload.items()))
    except Exception:
        return


def log_dataframe_shape(name, df):
    if not diagnostics_enabled():
        return
    try:
        rows, cols = df.shape
        memory_mb = float(df.memory_usage(deep=True).sum()) / (1024.0 * 1024.0)
        log_runtime_event("dataframe", name=name, rows=rows, columns=cols, memory_mb=f"{memory_mb:.3f}")
    except Exception:
        log_runtime_event("dataframe", name=name, rows="unknown", columns="unknown")


def log_figure_shape(section, fig):
    if not diagnostics_enabled():
        return
    try:
        trace_count = len(getattr(fig, "data", []) or [])
        json_length = len(fig.to_json())
        log_runtime_event("plotly_figure", section=section, traces=trace_count, json_length=json_length)
    except Exception:
        log_runtime_event("plotly_figure", section=section, traces="unknown", json_length="unknown")


def log_section_start(section):
    log_runtime_event("section_start", section=section)


def log_section_end(section):
    if diagnostics_enabled():
        try:
            gc.collect()
        except Exception:
            pass
    log_runtime_event("section_end", section=section)
