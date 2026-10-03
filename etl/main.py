"""Main pipeline: runs on GitHub Actions every 5 minutes."""
import sys, uuid, json, logging, traceback
from datetime import datetime, timezone

from sqlalchemy import text

from etl.db        import get_engine
from etl.extract   import extract
from etl.transform import to_dataframe, validate
from etl.load      import land_raw, upsert_prices


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("crypto")


def log_run(engine, run_id, status, rows=None, error=None, started=None, finished=None):
    with engine.begin() as conn:
        conn.execute(text(
            "insert into meta.pipeline_runs "
            "(run_id, started_at, finished_at, status, rows_loaded, error_message) "
            "values (:rid, :st, :fi, :status, :rows, :err) "
            "on conflict (run_id) do update set "
            "finished_at   = excluded.finished_at, "
            "status        = excluded.status, "
            "rows_loaded   = excluded.rows_loaded, "
            "error_message = excluded.error_message"
        ), {
            "rid": run_id, "st": started, "fi": finished,
            "status": status, "rows": rows, "err": error,
        })


def run() -> int:
    run_id  = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    engine  = get_engine()

    log_run(engine, run_id, "running", started=started)

    try:
        log.info("EXTRACT")
        coins = extract(top_n=20)
        log.info(f"  got {len(coins)} coins")

        log.info("TRANSFORM")
        df = to_dataframe(coins)
        validate(df)
        log.info(f"  {len(df)} clean rows")

        log.info("LOAD")
        land_raw(engine, coins, run_id)
        n = upsert_prices(engine, df)
        log.info(f"  saved {n} rows")

        log_run(engine, run_id, "success", rows=n,
                started=started, finished=datetime.now(timezone.utc))
        log.info("SUCCESS")
        return 0

    except Exception as exc:
        log.error(f"FAILED: {exc}")
        log.error(traceback.format_exc())
        log_run(engine, run_id, "failed", error=str(exc)[:500],
                started=started, finished=datetime.now(timezone.utc))
        return 1


if __name__ == "__main__":
    sys.exit(run())
