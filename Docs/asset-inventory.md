# Legacy asset inventory

This inventory records files with no references by exact filename in the
current Markdown, source, tests, or configuration. It is a review list, not
proof that a file is safe to delete: historical calibration examples and PCB
drawings may still be useful to maintainers. The inventory itself is excluded
when assessing those references.

| Asset | Approx. size | Note |
| --- | ---: | --- |
| `Docs/20191130_184738.jpg` | 75 KiB | Historical photo. |
| `Docs/20200105_124152.jpg` | 44 KiB | Historical photo. |
| `Docs/bracket-top.jpg` | 44 KiB | Bracket photo; bottom view is referenced in `HW/README.md`. |
| `HW/20191130_184738.jpg` | 75 KiB | Historical hardware photo; same name as a Docs image, contents differ. |
| `HW/Netcam_rear.jpg` | 75 KiB | Rear camera view; front view is referenced in `HW/README.md`. |
| `SW/GameData/dartshape.jpg` | 1 KiB | Old image with no exact reference found. |
| `SW/DartScoreEngine/BoardCalibration/cv2.jpg` | 122 KiB | Historical calibration intermediate. |
| `Docs/dartscore-presentation.pdf` | 3.2 MiB | Historical presentation, not a Markdown source file. |
| `Docs/dartscore_pcb_schema.pdf` | 49 KiB | Historical schematic, possibly useful with the Eagle board. |
| `Docs/dartscorestates.state.violet.html` | 78 KiB | Old diagram export. |
| `Docs/Re_ Method to Identify and Score Darts....eml` | 5.1 MiB | Archived email, not referenced by documentation or code. |

There are no byte-identical image duplicates among these assets. Keep them in
this documentation-only PR; decide whether to archive or remove historical
source material in a separate cleanup after inspecting the files. The current
README hero, calibration illustrations, and video replay fixtures are in use.
