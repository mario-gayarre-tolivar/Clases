"""Atomic file-based storage for pedagogical ML models and associated metadata."""

import json
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib  # type: ignore[import-untyped]

from tutoring.domain.analytics.feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

MODEL_FILENAME = "active_analyzer.joblib"
METADATA_FILENAME = "active_analyzer_meta.json"


@dataclass(frozen=True)
class ModelMetadata:
    """Diagnostic and evaluation metadata snapshot for a trained classical model."""

    version: int
    trained_at: datetime
    analyzer_name: str
    sample_count: int
    positive_count: int
    negative_count: int
    cv_f1_macro: float
    baseline_f1_macro: float
    dataset_hash: str
    feature_names: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to a JSON-serializable dictionary."""
        return {
            "version": self.version,
            "trained_at": self.trained_at.isoformat(),
            "analyzer_name": self.analyzer_name,
            "sample_count": self.sample_count,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "cv_f1_macro": self.cv_f1_macro,
            "baseline_f1_macro": self.baseline_f1_macro,
            "dataset_hash": self.dataset_hash,
            "feature_names": list(self.feature_names),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelMetadata":
        """Reconstruct ModelMetadata from a dictionary."""
        return cls(
            version=int(data["version"]),
            trained_at=datetime.fromisoformat(data["trained_at"]),
            analyzer_name=str(data["analyzer_name"]),
            sample_count=int(data["sample_count"]),
            positive_count=int(data["positive_count"]),
            negative_count=int(data["negative_count"]),
            cv_f1_macro=float(data["cv_f1_macro"]),
            baseline_f1_macro=float(data["baseline_f1_macro"]),
            dataset_hash=str(data["dataset_hash"]),
            feature_names=tuple(str(f) for f in data["feature_names"]),
        )


class ModelArtifactStore:
    """Atomic file persistence and schema validation for pedagogical ML models."""

    def __init__(self, model_dir: str | Path) -> None:
        self._model_dir = Path(model_dir)
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._model_path = self._model_dir / MODEL_FILENAME
        self._meta_path = self._model_dir / METADATA_FILENAME

    @property
    def model_path(self) -> Path:
        return self._model_path

    @property
    def meta_path(self) -> Path:
        return self._meta_path

    def save(self, model: Any, metadata: ModelMetadata) -> ModelMetadata:
        """Atomically persist classifier and metadata using temporary files and replace."""
        self._model_dir.mkdir(parents=True, exist_ok=True)

        tmp_model_fd, tmp_model_path_str = tempfile.mkstemp(
            dir=self._model_dir, prefix="tmp_model_", suffix=".joblib"
        )
        os.close(tmp_model_fd)
        tmp_model_path = Path(tmp_model_path_str)

        tmp_meta_fd, tmp_meta_path_str = tempfile.mkstemp(
            dir=self._model_dir, prefix="tmp_meta_", suffix=".json"
        )
        os.close(tmp_meta_fd)
        tmp_meta_path = Path(tmp_meta_path_str)

        try:
            joblib.dump(model, tmp_model_path)
            tmp_meta_path.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
            os.replace(tmp_model_path, self._model_path)
            os.replace(tmp_meta_path, self._meta_path)
        except Exception:
            if tmp_model_path.exists():
                tmp_model_path.unlink()
            if tmp_meta_path.exists():
                tmp_meta_path.unlink()
            raise

        return metadata

    def load_metadata(self) -> ModelMetadata | None:
        """Load and validate metadata, returning None if corrupted or schema mismatched."""
        if not self._meta_path.is_file():
            return None
        try:
            raw_text = self._meta_path.read_text(encoding="utf-8")
            data = json.loads(raw_text)
            if not isinstance(data, dict):
                logger.warning("Model metadata is not a JSON object: %s", self._meta_path)
                return None
            meta = ModelMetadata.from_dict(data)
            if tuple(meta.feature_names) != FeatureExtractor.FEATURE_NAMES:
                logger.warning(
                    "Model metadata feature names mismatch. Expected %s, got %s",
                    FeatureExtractor.FEATURE_NAMES,
                    meta.feature_names,
                )
                return None
            return meta
        except (OSError, ValueError, TypeError, KeyError) as exc:
            logger.warning("Failed to load model metadata from %s: %s", self._meta_path, exc)
            return None
        except Exception as exc:
            logger.warning(
                "Unexpected error loading model metadata from %s: %s", self._meta_path, exc
            )
            return None

    def load(self) -> tuple[Any, ModelMetadata] | None:
        """Load persisted model and metadata, returning None if missing, corrupted, or schema mismatch."""
        if not self._model_path.is_file() or not self._meta_path.is_file():
            return None
        meta = self.load_metadata()
        if meta is None:
            return None
        try:
            model = joblib.load(self._model_path)
            return model, meta
        except (OSError, ValueError, TypeError, KeyError) as exc:
            logger.warning("Failed to load model artifact from %s: %s", self._model_path, exc)
            return None
        except Exception as exc:
            logger.warning(
                "Unexpected error loading model artifact from %s: %s", self._model_path, exc
            )
            return None
