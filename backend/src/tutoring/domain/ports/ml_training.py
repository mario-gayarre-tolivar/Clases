"""Port contract for triggering machine learning model retraining."""

from typing import Protocol


class TrainingTriggerPort(Protocol):
    """Port interface for notifying external pipeline that fresh training data is available."""

    def notify_new_data(self) -> None:
        """Signal that new training examples (e.g. session attempts or exam results) are recorded."""
        ...
