"""Pure game rules and state, independent of cameras and presentation."""

from .service import GameService, GameSnapshot, ScoreEvent

__all__ = ["GameService", "GameSnapshot", "ScoreEvent"]
