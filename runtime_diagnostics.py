import gc
import datetime as _datetime
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

try:
    import pandas as pd
except Exception:
    pd = None


LOGGER = logging.getLogger("pbos.runtime")
if not LOGGER.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def diagnostics_enabled():
    return os.environ.get("PBOS_RUNTIME_DIAGNOSTICS", "").strip().lower() in {"1", "true", "yes", "on"}


def safe_table_mode_enabled():
    return os.environ.get("PBOS_SAFE_TABLE_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


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
        object_columns = int((df.dtypes == "object").sum()) if hasattr(df, "dtypes") else 0
        nested_cells = count_nested_cells(df)
        log_runtime_event("dataframe", name=name, rows=rows, columns=cols, memory_mb=f"{memory_mb:.3f}", object_columns=object_columns, nested_cells=nested_cells)
    except Exception:
        log_runtime_event("dataframe", name=name, rows="unknown", columns="unknown")


def count_nested_cells(df):
    try:
        return int(df.map(lambda value: isinstance(value, (dict, list, tuple, set))).to_numpy().sum())
    except Exception:
        return 0


def _display_scalar(value):
    if isinstance(value, (dict, list, tuple, set)):
        text = ", ".join(str(item) for item in value.items()) if isinstance(value, dict) else ", ".join(str(item) for item in value)
        return text[:500]
    if isinstance(value, (_datetime.date, _datetime.datetime)):
        return value.isoformat()
    try:
        if value is None or (pd is not None and pd.isna(value)):
            return ""
    except Exception:
        pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)[:500]


def normalize_display_dataframe(data, columns=None, max_rows=None):
    if pd is None:
        return data
    df = data.copy() if hasattr(data, "copy") else pd.DataFrame(data)
    if columns:
        existing_columns = [column for column in columns if column in df.columns]
        df = df[existing_columns].copy()
    else:
        df = pd.DataFrame(df).copy()
    df.columns = [str(column) for column in df.columns]
    if max_rows is not None:
        df = df.head(int(max_rows)).copy()
    for column in df.columns:
        df[column] = df[column].map(_display_scalar)
    return df


def render_display_dataframe(st, name, data, max_rows=100, **kwargs):
    display_df = normalize_display_dataframe(data, max_rows=max_rows)
    log_dataframe_shape(f"{name}:before", display_df)
    if safe_table_mode_enabled():
        st.table(display_df.head(min(len(display_df), max_rows)))
    else:
        st.dataframe(display_df, **kwargs)
    log_runtime_event("dataframe_rendered", name=name)
    return display_df


def render_display_editor(st, name, data, max_rows=100, **kwargs):
    display_df = normalize_display_dataframe(data, max_rows=max_rows)
    log_dataframe_shape(f"{name}:before_editor", display_df)
    if safe_table_mode_enabled():
        st.table(display_df.head(min(len(display_df), max_rows)))
        log_runtime_event("data_editor_safe_preview_rendered", name=name)
        return display_df
    edited_df = st.data_editor(display_df, **kwargs)
    log_runtime_event("data_editor_rendered", name=name)
    return edited_df


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
