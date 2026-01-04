import json
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

import duckdb

# Thread-local storage for database connections
_thread_local = threading.local()


class DevTrackDB:
    """DuckDB manager for DevTrack logging data."""

    @staticmethod
    def _validate_int(value: Any, name: str = "value", min_value: int = 0) -> int:
        """Validate and sanitize integer value to prevent SQL injection."""
        try:
            int_value = int(value)
            if int_value < min_value:
                raise ValueError(f"{name} must be >= {min_value}")
            return int_value
        except (ValueError, TypeError) as e:
            if isinstance(e, ValueError) and "must be" in str(e):
                raise
            raise ValueError(f"{name} must be a valid integer") from e

    def __init__(self, db_path: str = "devtrack_logs.db", read_only: bool = True):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self._lock = threading.Lock()
        self.read_only = read_only
        # Create initial connection for table creation (only if not read-only)
        if not read_only:
            self._init_conn = duckdb.connect(db_path)
            self._create_tables()
            self._init_conn.close()

    @property
    def conn(self):
        """Get thread-local database connection."""
        if not hasattr(_thread_local, "connection") or _thread_local.connection is None:
            _thread_local.connection = duckdb.connect(
                self.db_path, read_only=self.read_only
            )
        else:
            # Check if connection is closed and reconnect if needed
            try:
                # Try a simple query to check if connection is alive
                _thread_local.connection.execute("SELECT 1")
            except Exception:
                # Connection is closed, create a new one
                try:
                    _thread_local.connection.close()
                except Exception:
                    pass
                _thread_local.connection = duckdb.connect(
                    self.db_path, read_only=self.read_only
                )
        return _thread_local.connection

    def _create_tables(self):
        """Create the logs table if it doesn't exist."""
        # Create sequence for auto-incrementing ID

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_log_id'),
            path VARCHAR,
            path_pattern VARCHAR,
            method VARCHAR,
            status_code INTEGER,
            timestamp TIMESTAMP,
            client_ip VARCHAR,
            duration_ms DOUBLE,
            user_agent VARCHAR,
            referer VARCHAR,
            query_params VARCHAR,  -- JSON string
            path_params VARCHAR,   -- JSON string
            request_body VARCHAR,  -- JSON string
            response_size INTEGER,
            user_id VARCHAR,
            role VARCHAR,
            trace_id VARCHAR,
            client_identifier VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self._init_conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_log_id START 1")
        self._init_conn.execute(create_table_sql)

        # Migration: Rename client_identifier_hash to client_identifier
        try:
            self._init_conn.execute(
                "ALTER TABLE request_logs RENAME COLUMN "
                "client_identifier_hash TO client_identifier"
            )
        except Exception:
            # Column might not exist or already renamed, try adding client_identifier
            try:
                self._init_conn.execute(
                    "ALTER TABLE request_logs ADD COLUMN client_identifier VARCHAR"
                )
            except Exception:
                pass  # Column already exists

    def insert_log(self, log_data: Dict[str, Any]) -> int:
        """Insert a log entry into the database."""
        # Convert dict fields to JSON strings
        query_params_json = json.dumps(log_data.get("query_params", {}))
        path_params_json = json.dumps(log_data.get("path_params", {}))
        request_body_json = json.dumps(log_data.get("request_body", {}))

        # Parse timestamp
        timestamp = datetime.fromisoformat(log_data["timestamp"].replace("Z", "+00:00"))

        insert_sql = """
        INSERT INTO request_logs (
            path, path_pattern, method, status_code, timestamp, client_ip,
            duration_ms, user_agent, referer, query_params, path_params,
            request_body, response_size, user_id, role, trace_id, client_identifier
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        result = self.conn.execute(
            insert_sql,
            (
                log_data.get("path"),
                log_data.get("path_pattern"),
                log_data.get("method"),
                log_data.get("status_code"),
                timestamp,
                log_data.get("client_ip"),
                log_data.get("duration_ms"),
                log_data.get("user_agent"),
                log_data.get("referer"),
                query_params_json,
                path_params_json,
                request_body_json,
                log_data.get("response_size"),
                log_data.get("user_id"),
                log_data.get("role"),
                log_data.get("trace_id"),
                log_data.get("client_identifier")
                or log_data.get("client_identifier_hash"),
            ),
        )

        # Get the ID of the last inserted row
        # Note: DuckDB auto-commits transactions
        result = self.conn.execute(
            "SELECT id FROM request_logs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else None

    def _safe_json_loads(self, value: Any, default: Any = None) -> Any:
        """Safely parse JSON string, returning default on error."""
        if value is None:
            return default if default is not None else {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            if not value.strip():
                return default if default is not None else {}
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default if default is not None else {}
        return default if default is not None else {}

    def _format_log_dict(self, log_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Format a log dictionary by parsing JSON fields and formatting timestamp."""
        # Convert JSON strings back to dicts (handle empty/invalid JSON)
        log_dict["query_params"] = self._safe_json_loads(log_dict.get("query_params"))
        log_dict["path_params"] = self._safe_json_loads(log_dict.get("path_params"))
        log_dict["request_body"] = self._safe_json_loads(log_dict.get("request_body"))
        # Convert timestamp back to ISO format
        if log_dict.get("timestamp"):
            if hasattr(log_dict["timestamp"], "isoformat"):
                log_dict["timestamp"] = log_dict["timestamp"].isoformat()
            else:
                log_dict["timestamp"] = str(log_dict["timestamp"])
        return log_dict

    def get_all_logs(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve all logs from the database."""
        sql = "SELECT * FROM request_logs ORDER BY created_at DESC"
        if limit:
            # Validate and sanitize limit and offset to prevent SQL injection
            limit_int = int(limit)
            offset_int = int(offset)
            if limit_int < 0 or offset_int < 0:
                raise ValueError("limit and offset must be non-negative integers")
            sql += f" LIMIT {limit_int} OFFSET {offset_int}"

        # Execute query to get description first, then fetch results
        cursor = self.conn.execute(sql)
        # Get column names from description
        try:
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else None
            )
        except Exception:
            columns = None

        # If we couldn't get columns from description, use known column names
        if not columns or (len(columns) == 1 and columns[0] in ["1", "NUMBER"]):
            columns = [
                "id",
                "path",
                "path_pattern",
                "method",
                "status_code",
                "timestamp",
                "client_ip",
                "duration_ms",
                "user_agent",
                "referer",
                "query_params",
                "path_params",
                "request_body",
                "response_size",
                "user_id",
                "role",
                "trace_id",
                "client_identifier",
                "created_at",
            ]

        # Fetch all results
        result = cursor.fetchall()

        logs = []
        for row in result:
            log_dict = dict(zip(columns, row))
            log_dict = self._format_log_dict(log_dict)
            logs.append(log_dict)

        return logs

    def get_logs_count(self) -> int:
        """Get the total count of logs in the database."""
        result = self.conn.execute("SELECT COUNT(*) FROM request_logs").fetchone()
        return result[0]

    def tables_exist(self) -> bool:
        """Check if database tables exist (read-only check)."""
        try:
            # Try to query the table - will fail if it doesn't exist
            self.conn.execute("SELECT 1 FROM request_logs LIMIT 1")
            return True
        except Exception:
            return False

    def get_logs_by_path(
        self, path_pattern: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get logs filtered by path pattern."""
        sql = (
            "SELECT * FROM request_logs WHERE path_pattern = ? ORDER BY created_at DESC"
        )
        if limit:
            # Validate and sanitize limit to prevent SQL injection
            limit_int = int(limit)
            if limit_int < 0:
                raise ValueError("limit must be a non-negative integer")
            sql += f" LIMIT {limit_int}"

        # path_pattern is parameterized with ? placeholder - safe from SQL injection
        # nosemgrep: python.lang.security.audit.sql-injection
        cursor = self.conn.execute(sql, (path_pattern,))
        result = cursor.fetchall()

        # Get column names from description, with fallback for DuckDB quirks
        try:
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else None
            )
        except Exception:
            columns = None

        # If we couldn't get columns from description, use known column names
        if not columns or (len(columns) == 1 and columns[0] in ["1", "NUMBER"]):
            columns = [
                "id",
                "path",
                "path_pattern",
                "method",
                "status_code",
                "timestamp",
                "client_ip",
                "duration_ms",
                "user_agent",
                "referer",
                "query_params",
                "path_params",
                "request_body",
                "response_size",
                "user_id",
                "role",
                "trace_id",
                "client_identifier",
                "created_at",
            ]

        logs = []
        for row in result:
            log_dict = dict(zip(columns, row))
            log_dict = self._format_log_dict(log_dict)
            logs.append(log_dict)

        return logs

    def get_logs_by_status_code(
        self, status_code: int, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get logs filtered by status code."""
        sql = (
            "SELECT * FROM request_logs WHERE status_code = ? ORDER BY created_at DESC"
        )
        if limit:
            # Validate and sanitize limit to prevent SQL injection
            limit_int = int(limit)
            if limit_int < 0:
                raise ValueError("limit must be a non-negative integer")
            sql += f" LIMIT {limit_int}"

        # status_code is parameterized with ? placeholder - safe from SQL injection
        # nosemgrep: python.lang.security.audit.sql-injection
        cursor = self.conn.execute(sql, (status_code,))
        result = cursor.fetchall()

        # Get column names from description, with fallback for DuckDB quirks
        try:
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else None
            )
        except Exception:
            columns = None

        # If we couldn't get columns from description, use known column names
        if not columns or (len(columns) == 1 and columns[0] in ["1", "NUMBER"]):
            columns = [
                "id",
                "path",
                "path_pattern",
                "method",
                "status_code",
                "timestamp",
                "client_ip",
                "duration_ms",
                "user_agent",
                "referer",
                "query_params",
                "path_params",
                "request_body",
                "response_size",
                "user_id",
                "role",
                "trace_id",
                "client_identifier",
                "created_at",
            ]

        logs = []
        for row in result:
            log_dict = dict(zip(columns, row))
            log_dict = self._format_log_dict(log_dict)
            logs.append(log_dict)

        return logs

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics from the logs."""
        stats_sql = """
        SELECT
            COUNT(*) as total_requests,
            COUNT(DISTINCT path_pattern) as unique_endpoints,
            AVG(duration_ms) as avg_duration_ms,
            MIN(duration_ms) as min_duration_ms,
            MAX(duration_ms) as max_duration_ms,
            COUNT(CASE WHEN status_code >= 200 AND status_code < 300
                THEN 1 END) as success_count,
            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
        FROM request_logs
        """

        cursor = self.conn.execute(stats_sql)
        result = cursor.fetchone()

        # Get column names from description, with fallback for DuckDB quirks
        try:
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else None
            )
        except Exception:
            columns = None

        # If we couldn't get columns from description or got invalid column names,
        # use the known column names from the SQL query
        if not columns or (len(columns) == 1 and columns[0] in ["1", "NUMBER"]):
            columns = [
                "total_requests",
                "unique_endpoints",
                "avg_duration_ms",
                "min_duration_ms",
                "max_duration_ms",
                "success_count",
                "error_count",
            ]

        return dict(zip(columns, result))

    def delete_all_logs(self) -> int:
        """Delete all logs from the database."""
        # Get count before deletion
        count_result = self.conn.execute("SELECT COUNT(*) FROM request_logs").fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete all logs
        self.conn.execute("DELETE FROM request_logs")

        return count_before

    def reset_sequence(self) -> None:
        """Reset the sequence to start from 1."""
        try:
            # Try to reset the sequence
            self.conn.execute("ALTER SEQUENCE seq_log_id RESTART WITH 1")
        except Exception:
            # If sequence doesn't exist or can't be reset, try to recreate it
            try:
                self.conn.execute("DROP SEQUENCE IF EXISTS seq_log_id")
                self.conn.execute("CREATE SEQUENCE seq_log_id START 1")
            except Exception:
                pass  # Ignore if sequence operations fail

    def delete_logs_by_path(self, path_pattern: str) -> int:
        """Delete logs filtered by path pattern."""
        # Get count before deletion
        count_result = self.conn.execute(
            "SELECT COUNT(*) FROM request_logs WHERE path_pattern = ?", (path_pattern,)
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete logs
        self.conn.execute(
            "DELETE FROM request_logs WHERE path_pattern = ?", (path_pattern,)
        )

        return count_before

    def delete_logs_by_status_code(self, status_code: int) -> int:
        """Delete logs filtered by status code."""
        # Get count before deletion
        count_result = self.conn.execute(
            "SELECT COUNT(*) FROM request_logs WHERE status_code = ?", (status_code,)
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete logs
        self.conn.execute(
            "DELETE FROM request_logs WHERE status_code = ?", (status_code,)
        )

        return count_before

    def delete_logs_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> int:
        """Delete logs within a date range."""
        # Get count before deletion
        count_result = self.conn.execute(
            "SELECT COUNT(*) FROM request_logs WHERE timestamp BETWEEN ? AND ?",
            (start_date, end_date),
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete logs
        self.conn.execute(
            "DELETE FROM request_logs WHERE timestamp BETWEEN ? AND ?",
            (start_date, end_date),
        )

        return count_before

    def delete_logs_older_than(self, days: int) -> int:
        """Delete logs older than specified number of days."""
        # Validate and sanitize days to prevent SQL injection
        days_int = self._validate_int(days, "days", min_value=0)

        # Get count before deletion
        # days_int is validated as integer - safe from SQL injection
        # nosemgrep: python.lang.security.audit.sql-injection
        count_result = self.conn.execute(
            f"SELECT COUNT(*) FROM request_logs WHERE timestamp < "
            f"(CURRENT_TIMESTAMP - INTERVAL '{days_int} days')"
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete logs
        # days_int is validated as integer - safe from SQL injection
        # nosemgrep: python.lang.security.audit.sql-injection
        self.conn.execute(
            f"DELETE FROM request_logs WHERE timestamp < "
            f"(CURRENT_TIMESTAMP - INTERVAL '{days_int} days')"
        )

        return count_before

    def delete_logs_by_id(self, log_id: int) -> int:
        """Delete a specific log by ID."""
        # Get count before deletion
        count_result = self.conn.execute(
            "SELECT COUNT(*) FROM request_logs WHERE id = ?", (log_id,)
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete log
        self.conn.execute("DELETE FROM request_logs WHERE id = ?", (log_id,))

        return count_before

    def delete_logs_by_ids(self, log_ids: List[int]) -> int:
        """Delete multiple logs by their IDs."""
        if not log_ids:
            return 0

        # Get count before deletion
        placeholders = ",".join(["?" for _ in log_ids])
        count_result = self.conn.execute(
            f"SELECT COUNT(*) FROM request_logs WHERE id IN ({placeholders})", log_ids
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete logs
        self.conn.execute(
            f"DELETE FROM request_logs WHERE id IN ({placeholders})", log_ids
        )

        return count_before

    def get_traffic_over_time(
        self, hours: int = 24, interval_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """Get traffic counts grouped by time intervals."""
        # Validate and sanitize hours to prevent SQL injection
        hours_int = self._validate_int(hours, "hours", min_value=0)

        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            COUNT(*) as request_count
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
        GROUP BY date_trunc('minute', timestamp)
        ORDER BY time_bucket ASC
        """
        result = self.conn.execute(sql).fetchall()
        return [
            {
                "time_bucket": (
                    row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0])
                ),
                "request_count": row[1],
            }
            for row in result
        ]

    def get_error_trends(
        self, hours: int = 24, interval_minutes: int = 5
    ) -> Dict[str, Any]:
        """Get error trends including failure rates over time and top failing routes."""
        # Validate and sanitize hours to prevent SQL injection
        hours_int = self._validate_int(hours, "hours", min_value=0)

        # Error rates over time
        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            COUNT(*) as total_requests,
            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
        GROUP BY date_trunc('minute', timestamp)
        ORDER BY time_bucket ASC
        """
        result = self.conn.execute(sql).fetchall()
        error_trends = [
            {
                "time_bucket": (
                    row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0])
                ),
                "total_requests": row[1],
                "error_count": row[2],
                "error_rate": (row[2] / row[1] * 100) if row[1] > 0 else 0,
            }
            for row in result
        ]

        # Top failing routes
        total_errors = self.conn.execute(
            "SELECT COUNT(*) FROM request_logs WHERE status_code >= 400"
        ).fetchone()[0]

        top_failing_sql = """
        SELECT
            path_pattern,
            method,
            COUNT(*) as error_count
        FROM request_logs
        WHERE status_code >= 400
        GROUP BY path_pattern, method
        ORDER BY error_count DESC
        LIMIT 10
        """
        top_failing_result = self.conn.execute(top_failing_sql).fetchall()
        top_failing_routes = [
            {
                "route": f"{row[1]} {row[0]}" if row[0] else "-",
                "error_count": row[2],
                "error_rate": (
                    round((row[2] / total_errors * 100), 2) if total_errors > 0 else 0
                ),
            }
            for row in top_failing_result
        ]

        return {
            "error_trends": error_trends,
            "top_failing_routes": top_failing_routes,
        }

    def get_performance_metrics(
        self, hours: int = 24, interval_minutes: int = 5
    ) -> Dict[str, Any]:
        """Get performance metrics including p50, p95, p99 latency over time."""
        import statistics

        # Validate and sanitize hours to prevent SQL injection
        hours_int = self._validate_int(hours, "hours", min_value=0)

        # Get all duration_ms values grouped by time bucket
        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            duration_ms
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
            AND duration_ms IS NOT NULL
        ORDER BY time_bucket ASC, duration_ms ASC
        """
        result = self.conn.execute(sql).fetchall()

        # Group by time bucket and calculate percentiles
        from collections import defaultdict

        time_buckets = defaultdict(list)
        for row in result:
            time_bucket = (
                row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0])
            )
            duration = row[1]
            if duration is not None:
                time_buckets[time_bucket].append(float(duration))

        # Calculate percentiles for each time bucket
        performance_metrics = []
        for time_bucket, durations in sorted(time_buckets.items()):
            if durations:
                sorted_durations = sorted(durations)
                n = len(sorted_durations)
                p50_idx = int(n * 0.50)
                p95_idx = int(n * 0.95)
                p99_idx = int(n * 0.99)

                performance_metrics.append(
                    {
                        "time_bucket": time_bucket,
                        "p50": round(
                            (
                                sorted_durations[p50_idx]
                                if p50_idx < n
                                else sorted_durations[-1]
                            ),
                            2,
                        ),
                        "p95": round(
                            (
                                sorted_durations[p95_idx]
                                if p95_idx < n
                                else sorted_durations[-1]
                            ),
                            2,
                        ),
                        "p99": round(
                            (
                                sorted_durations[p99_idx]
                                if p99_idx < n
                                else sorted_durations[-1]
                            ),
                            2,
                        ),
                        "avg": round(statistics.mean(durations), 2),
                    }
                )

        # Overall percentiles
        # hours_int already validated above
        overall_sql = f"""
        SELECT duration_ms
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
            AND duration_ms IS NOT NULL
        ORDER BY duration_ms ASC
        """
        overall_result = self.conn.execute(overall_sql).fetchall()
        overall_durations = [
            float(row[0]) for row in overall_result if row[0] is not None
        ]

        overall_metrics = {}
        if overall_durations:
            sorted_overall = sorted(overall_durations)
            n = len(sorted_overall)
            p50_idx = int(n * 0.50)
            p95_idx = int(n * 0.95)
            p99_idx = int(n * 0.99)

            overall_metrics = {
                "p50": round(
                    sorted_overall[p50_idx] if p50_idx < n else sorted_overall[-1], 2
                ),
                "p95": round(
                    sorted_overall[p95_idx] if p95_idx < n else sorted_overall[-1], 2
                ),
                "p99": round(
                    sorted_overall[p99_idx] if p99_idx < n else sorted_overall[-1], 2
                ),
                "avg": round(statistics.mean(overall_durations), 2),
            }
        else:
            overall_metrics = {
                "p50": None,
                "p95": None,
                "p99": None,
                "avg": None,
            }

        return {
            "latency_over_time": performance_metrics,
            "overall_stats": overall_metrics,
        }

    def get_consumer_segments(self, hours: int = 24) -> Dict[str, Any]:
        """Get consumer segmentation data grouped by client identifier."""
        # Validate and sanitize hours to prevent SQL injection
        hours_int = self._validate_int(hours, "hours", min_value=0)

        # Get unique clients and their stats, including most recent IP
        sql = f"""
        SELECT
            client_identifier,
            COUNT(*) as request_count,
            COUNT(DISTINCT path_pattern) as unique_endpoints,
            AVG(duration_ms) as avg_latency,
            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen,
            (SELECT client_ip FROM request_logs r2
             WHERE r2.client_identifier = request_logs.client_identifier
             AND r2.timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
             ORDER BY r2.timestamp DESC LIMIT 1) as latest_ip
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
            AND client_identifier IS NOT NULL
        GROUP BY client_identifier
        ORDER BY request_count DESC
        LIMIT 50
        """
        result = self.conn.execute(sql).fetchall()

        segments = []
        for row in result:
            segments.append(
                {
                    # Original client identifier (kept key name for API compatibility)
                    "client_identifier_hash": row[0],
                    "client_identifier": row[0],  # Also include as client_identifier
                    "request_count": row[1],
                    "unique_endpoints": row[2],
                    "avg_latency_ms": round(row[3], 2) if row[3] is not None else None,
                    "error_count": row[4],
                    "error_rate": (
                        round((row[4] / row[1] * 100), 2) if row[1] > 0 else 0
                    ),
                    "first_seen": (
                        row[5].isoformat()
                        if hasattr(row[5], "isoformat")
                        else str(row[5])
                    ),
                    "last_seen": (
                        row[6].isoformat()
                        if hasattr(row[6], "isoformat")
                        else str(row[6])
                    ),
                    "latest_ip": row[7] if row[7] and row[7] != "unknown" else None,
                }
            )

        # Get total unique clients
        # hours_int already validated above
        total_clients_sql = f"""
        SELECT COUNT(DISTINCT client_identifier)
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
            AND client_identifier IS NOT NULL
        """
        total_clients = self.conn.execute(total_clients_sql).fetchone()[0] or 0

        # Get client identification source breakdown
        source_sql = f"""
        SELECT
            CASE
                WHEN client_identifier IS NULL THEN 'unknown'
                ELSE 'identified'
            END as source_type,
            COUNT(DISTINCT client_identifier) as client_count,
            COUNT(*) as request_count
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
        GROUP BY source_type
        """
        source_result = self.conn.execute(source_sql).fetchall()
        source_breakdown = {
            row[0]: {
                "client_count": row[1],
                "request_count": row[2],
            }
            for row in source_result
        }

        return {
            "segments": segments,
            "total_unique_clients": total_clients,
            "source_breakdown": source_breakdown,
        }

    def get_client_metrics(self, client_hash: str, hours: int = 24) -> Dict[str, Any]:
        """Get detailed metrics for a specific client."""
        # Validate and sanitize hours to prevent SQL injection
        hours_int = self._validate_int(hours, "hours", min_value=0)

        sql = f"""
        SELECT
            COUNT(*) as request_count,
            COUNT(DISTINCT path_pattern) as unique_endpoints,
            AVG(duration_ms) as avg_latency,
            MIN(duration_ms) as min_latency,
            MAX(duration_ms) as max_latency,
            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count,
            COUNT(CASE WHEN status_code >= 200 AND status_code < 300
                THEN 1 END) as success_count
        FROM request_logs
        WHERE client_identifier = ?
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
        """
        result = self.conn.execute(sql, (client_hash,)).fetchone()

        if not result or result[0] == 0:
            return {"error": "Client not found or no data"}

        return {
            "client_hash": client_hash,
            "request_count": result[0],
            "unique_endpoints": result[1],
            "avg_latency": round(result[2], 2) if result[2] is not None else None,
            "min_latency": round(result[3], 2) if result[3] is not None else None,
            "max_latency": round(result[4], 2) if result[4] is not None else None,
            "error_count": result[5],
            "success_count": result[6],
            "error_rate": (
                round((result[5] / result[0] * 100), 2) if result[0] > 0 else 0
            ),
        }

    def get_client_traffic_over_time(
        self, client_hash: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get traffic over time for a specific client."""
        # Validate and sanitize hours to prevent SQL injection
        hours_int = self._validate_int(hours, "hours", min_value=0)

        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            COUNT(*) as request_count
        FROM request_logs
        WHERE client_identifier = ?
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours_int} hours'
        GROUP BY date_trunc('minute', timestamp)
        ORDER BY time_bucket ASC
        """
        result = self.conn.execute(sql, (client_hash,)).fetchall()
        return [
            {
                "timestamp": (
                    row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0])
                ),
                "count": row[1],
            }
            for row in result
        ]

    def close(self):
        """Close the database connection."""
        if (
            hasattr(_thread_local, "connection")
            and _thread_local.connection is not None
        ):
            try:
                _thread_local.connection.close()
            except Exception:
                pass
            _thread_local.connection = None

    def __del__(self):
        """Ensure connection is closed when object is destroyed."""
        # Don't access self.conn property here as it may try to create a new connection
        # Instead, directly check and close thread-local connection
        if (
            hasattr(_thread_local, "connection")
            and _thread_local.connection is not None
        ):
            try:
                _thread_local.connection.close()
            except Exception:
                pass
            _thread_local.connection = None


# Global database instance
_db_instance: Optional[DevTrackDB] = None


def get_db(read_only: bool = True) -> DevTrackDB:
    """Get the global database instance."""
    global _db_instance
    # If instance exists but has different read_only setting, recreate it
    # BUT: If we have an existing instance with write access, we can use it
    # for reads too (DuckDB allows read operations on write connections)
    if _db_instance is not None:
        if _db_instance.read_only != read_only:
            # If existing instance is write mode and we need read, we can use it
            if not _db_instance.read_only and read_only:
                # Use existing write connection for read operations
                # (allowed by DuckDB)
                return _db_instance
            # If existing instance is read-only and we need write, recreate
            elif _db_instance.read_only and not read_only:
                _db_instance.close()
                _db_instance = None
    if _db_instance is None:
        _db_instance = DevTrackDB(read_only=read_only)
    return _db_instance


def init_db(db_path: str = "devtrack_logs.db", read_only: bool = True):
    """Initialize the database with a custom path."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
    _db_instance = DevTrackDB(db_path, read_only=read_only)
    return _db_instance
