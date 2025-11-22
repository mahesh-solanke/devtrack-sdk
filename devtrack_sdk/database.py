import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import duckdb


class DevTrackDB:
    """DuckDB manager for DevTrack logging data."""

    def __init__(self, db_path: str = "devtrack_logs.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._create_tables()

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
            client_identifier_hash VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_log_id START 1")
        self.conn.execute(create_table_sql)

        # Add client_identifier_hash column if it doesn't exist (migration)
        try:
            self.conn.execute(
                "ALTER TABLE request_logs ADD COLUMN client_identifier_hash VARCHAR"
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
            request_body, response_size, user_id, role, trace_id, client_identifier_hash
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
                log_data.get("client_identifier_hash"),
            ),
        )

        # Get the ID of the last inserted row
        # Note: DuckDB auto-commits transactions
        result = self.conn.execute(
            "SELECT id FROM request_logs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else None

    def get_all_logs(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve all logs from the database."""
        sql = "SELECT * FROM request_logs ORDER BY created_at DESC"
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"

        result = self.conn.execute(sql).fetchall()
        columns = [desc[0] for desc in self.conn.description]

        logs = []
        for row in result:
            log_dict = dict(zip(columns, row))
            # Convert JSON strings back to dicts
            log_dict["query_params"] = json.loads(log_dict["query_params"])
            log_dict["path_params"] = json.loads(log_dict["path_params"])
            log_dict["request_body"] = json.loads(log_dict["request_body"])
            # Convert timestamp back to ISO format
            log_dict["timestamp"] = log_dict["timestamp"].isoformat()
            logs.append(log_dict)

        return logs

    def get_logs_count(self) -> int:
        """Get the total count of logs in the database."""
        result = self.conn.execute("SELECT COUNT(*) FROM request_logs").fetchone()
        return result[0]

    def get_logs_by_path(
        self, path_pattern: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get logs filtered by path pattern."""
        sql = (
            "SELECT * FROM request_logs WHERE path_pattern = ? ORDER BY created_at DESC"
        )
        if limit:
            sql += f" LIMIT {limit}"

        result = self.conn.execute(sql, (path_pattern,)).fetchall()
        columns = [desc[0] for desc in self.conn.description]

        logs = []
        for row in result:
            log_dict = dict(zip(columns, row))
            # Convert JSON strings back to dicts
            log_dict["query_params"] = json.loads(log_dict["query_params"])
            log_dict["path_params"] = json.loads(log_dict["path_params"])
            log_dict["request_body"] = json.loads(log_dict["request_body"])
            # Convert timestamp back to ISO format
            log_dict["timestamp"] = log_dict["timestamp"].isoformat()
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
            sql += f" LIMIT {limit}"

        result = self.conn.execute(sql, (status_code,)).fetchall()
        columns = [desc[0] for desc in self.conn.description]

        logs = []
        for row in result:
            log_dict = dict(zip(columns, row))
            # Convert JSON strings back to dicts
            log_dict["query_params"] = json.loads(log_dict["query_params"])
            log_dict["path_params"] = json.loads(log_dict["path_params"])
            log_dict["request_body"] = json.loads(log_dict["request_body"])
            # Convert timestamp back to ISO format
            log_dict["timestamp"] = log_dict["timestamp"].isoformat()
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

        result = self.conn.execute(stats_sql).fetchone()
        columns = [desc[0] for desc in self.conn.description]

        return dict(zip(columns, result))

    def delete_all_logs(self) -> int:
        """Delete all logs from the database."""
        # Get count before deletion
        count_result = self.conn.execute("SELECT COUNT(*) FROM request_logs").fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete all logs
        self.conn.execute("DELETE FROM request_logs")

        return count_before

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
        # Get count before deletion
        count_result = self.conn.execute(
            "SELECT COUNT(*) FROM request_logs WHERE timestamp < "
            "(CURRENT_TIMESTAMP - INTERVAL '{} days')".format(days)
        ).fetchone()
        count_before = count_result[0] if count_result else 0

        # Delete logs
        self.conn.execute(
            "DELETE FROM request_logs WHERE timestamp < "
            "(CURRENT_TIMESTAMP - INTERVAL '{} days')".format(days)
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
        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            COUNT(*) as request_count
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
        GROUP BY date_trunc('minute', timestamp)
        ORDER BY time_bucket ASC
        """
        result = self.conn.execute(sql).fetchall()
        return [
            {
                "timestamp": (
                    row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0])
                ),
                "count": row[1],
            }
            for row in result
        ]

    def get_error_trends(
        self, hours: int = 24, interval_minutes: int = 5
    ) -> Dict[str, Any]:
        """Get error trends including failure rates over time and top failing routes."""
        # Error rates over time
        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            COUNT(*) as total_requests,
            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
        GROUP BY date_trunc('minute', timestamp)
        ORDER BY time_bucket ASC
        """
        result = self.conn.execute(sql).fetchall()
        error_trends = [
            {
                "timestamp": (
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
                "path": row[0],
                "method": row[1],
                "error_count": row[2],
                "error_percentage": (
                    round((row[2] / total_errors * 100), 2) if total_errors > 0 else 0
                ),
            }
            for row in top_failing_result
        ]

        return {
            "trends": error_trends,
            "top_failing_routes": top_failing_routes,
        }

    def get_performance_metrics(
        self, hours: int = 24, interval_minutes: int = 5
    ) -> Dict[str, Any]:
        """Get performance metrics including p50, p95, p99 latency over time."""
        import statistics

        # Get all duration_ms values grouped by time bucket
        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            duration_ms
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
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
                        "timestamp": time_bucket,
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
        overall_sql = f"""
        SELECT duration_ms
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
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
            "over_time": performance_metrics,
            "overall": overall_metrics,
        }

    def get_consumer_segments(self, hours: int = 24) -> Dict[str, Any]:
        """Get consumer segmentation data grouped by client identifier."""
        # Get unique clients and their stats, including most recent IP
        sql = f"""
        SELECT
            client_identifier_hash,
            COUNT(*) as request_count,
            COUNT(DISTINCT path_pattern) as unique_endpoints,
            AVG(duration_ms) as avg_latency,
            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen,
            (SELECT client_ip FROM request_logs r2
             WHERE r2.client_identifier_hash = request_logs.client_identifier_hash
             AND r2.timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
             ORDER BY r2.timestamp DESC LIMIT 1) as latest_ip
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
            AND client_identifier_hash IS NOT NULL
        GROUP BY client_identifier_hash
        ORDER BY request_count DESC
        LIMIT 50
        """
        result = self.conn.execute(sql).fetchall()

        segments = []
        for row in result:
            segments.append(
                {
                    "client_hash": row[0],
                    "request_count": row[1],
                    "unique_endpoints": row[2],
                    "avg_latency": round(row[3], 2) if row[3] is not None else None,
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
                    "public_ip": row[7] if row[7] and row[7] != "unknown" else None,
                }
            )

        # Get total unique clients
        total_clients_sql = f"""
        SELECT COUNT(DISTINCT client_identifier_hash)
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
            AND client_identifier_hash IS NOT NULL
        """
        total_clients = self.conn.execute(total_clients_sql).fetchone()[0] or 0

        # Get client identification source breakdown
        source_sql = f"""
        SELECT
            CASE
                WHEN client_identifier_hash IS NULL THEN 'unknown'
                ELSE 'identified'
            END as source_type,
            COUNT(DISTINCT client_identifier_hash) as client_count,
            COUNT(*) as request_count
        FROM request_logs
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
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
        WHERE client_identifier_hash = ?
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
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
        sql = f"""
        SELECT
            date_trunc('minute', timestamp) as time_bucket,
            COUNT(*) as request_count
        FROM request_logs
        WHERE client_identifier_hash = ?
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '{hours} hours'
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
        self.conn.close()

    def __del__(self):
        """Ensure connection is closed when object is destroyed."""
        if hasattr(self, "conn"):
            self.close()


# Global database instance
_db_instance: Optional[DevTrackDB] = None


def get_db() -> DevTrackDB:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DevTrackDB()
    return _db_instance


def init_db(db_path: str = "devtrack_logs.db"):
    """Initialize the database with a custom path."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
    _db_instance = DevTrackDB(db_path)
    return _db_instance
