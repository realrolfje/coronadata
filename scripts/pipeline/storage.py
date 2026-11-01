from abc import ABC, abstractmethod
from collections import defaultdict
import json
from pathlib import Path
import sqlite3

from .models import Observation, ParserResult


class ObservationStore(ABC):
    @abstractmethod
    def write(self, result: ParserResult) -> int:
        """Store observations and return the number newly inserted."""

    @abstractmethod
    def daily_average(self, source_id: str, metric: str) -> list[tuple[str, float]]:
        """Return an average per observation date, ordered by date."""


class MemoryObservationStore(ObservationStore):
    def __init__(self):
        self._observations = {}

    @staticmethod
    def _key(observation):
        dimensions = json.dumps(observation.dimensions, sort_keys=True, separators=(",", ":"))
        return (
            observation.source_id,
            observation.metric,
            observation.date,
            observation.geography,
            dimensions,
        )

    def write(self, result):
        before = len(self._observations)
        for observation in result.observations:
            self._observations[self._key(observation)] = observation
        return len(self._observations) - before

    def daily_average(self, source_id, metric):
        values = defaultdict(list)
        for observation in self._observations.values():
            if observation.source_id == source_id and observation.metric == metric:
                values[observation.date].append(observation.value)
        return [
            (date, sum(items) / len(items))
            for date, items in sorted(values.items())
        ]


class SQLiteObservationStore(ObservationStore):
    def __init__(self, filename):
        self.filename = Path(filename)
        self.connection = sqlite3.connect(self.filename)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                source_id TEXT NOT NULL,
                metric TEXT NOT NULL,
                observation_date TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                geography TEXT NOT NULL,
                publication_date TEXT,
                dimensions_json TEXT NOT NULL,
                PRIMARY KEY (
                    source_id, metric, observation_date, geography, dimensions_json
                )
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS imports (
                source_id TEXT NOT NULL,
                raw_sha256 TEXT NOT NULL,
                publication_date TEXT,
                newest_observation TEXT,
                PRIMARY KEY (source_id, raw_sha256)
            )
            """
        )

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def write(self, result):
        rows = [
            (
                observation.source_id,
                observation.metric,
                observation.date,
                observation.value,
                observation.unit,
                observation.geography,
                observation.publication_date,
                json.dumps(
                    observation.dimensions, sort_keys=True, separators=(",", ":")
                ),
            )
            for observation in result.observations
        ]
        before = self.connection.total_changes
        self.connection.executemany(
            """
            INSERT OR IGNORE INTO observations (
                source_id, metric, observation_date, value, unit, geography,
                publication_date, dimensions_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        raw_sha256 = result.provenance.get("sha256")
        if raw_sha256:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO imports (
                    source_id, raw_sha256, publication_date, newest_observation
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    result.source_id,
                    raw_sha256,
                    result.publication_date,
                    result.newest_observation,
                ),
            )
        self.connection.commit()
        return self.connection.total_changes - before

    def daily_average(self, source_id, metric):
        return list(
            self.connection.execute(
                """
                SELECT observation_date, AVG(value)
                FROM observations
                WHERE source_id = ? AND metric = ?
                GROUP BY observation_date
                ORDER BY observation_date
                """,
                (source_id, metric),
            )
        )
