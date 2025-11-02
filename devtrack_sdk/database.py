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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_log_id START 1")
        self.conn.execute(create_table_sql)

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
            request_body, response_size, user_id, role, trace_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )

        # Get the ID of the last inserted row
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
