# GameData

This describes the historical single-camera implementation, which planned to
save calibration and game data as Python pickle structures. The new engine uses
a separate SQLite action journal; see [durable game session](../../Docs/durable-game-session.md).

## 1: Install settings
Saved calibration settings to be reused between games. Without this data the calibration makes a 'cold-start'
wich means that the user has to confirm the settings or change lightning conditions etc

## 2: Saved Game data
Saved game data will contain previous players, high-score, saved games etc....
