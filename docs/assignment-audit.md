# Assignment 2 deliverable audit

Source: `Lec#3.pdf`, pages 26, 28 and 29 (user-supplied lecture). Reviewed 2026-09-24. The slide lists Sunday September 27 as the due date.

| Requirement | Evidence | Status / remaining work |
|---|---|---|
| Animated simulation in MOV or MP4 — 30%; accuracy and visualization quality | 70-second 4K/24 fps director edit and previous 1080p movies | Format satisfied. Grade-level musical accuracy is not established: choreography is chart-guided and onset-aligned, not a verified note-for-note transcription. |
| Internally referenced GH — 10%; functionality, legibility, efficiency | `grasshopper/Birdland-Robots.gh`; geometry, event panels and solver source embedded | Reloaded and solved. Requires installed Robots/UniversalRobot and GhPython, but no external geometry or timing file. Renderer/camera effects are separate presentation scripts. |
| Pseudocode diagram + maximum one paragraph of design intent — 15%; clarity and completeness | `docs/Birdland-Pseudocode.pdf` | Supplied; revised to explain final 70-second movie and optional MIDI workflow. |
| Design a simulation and execute a toolpath — objective (partners) | Inverse-kinematics simulation only | Not physically executed; no controller-ready program or execution evidence. Confirm instructor's execution expectation and lab process. |
| Quiz — 30% | Not part of this project | Completion unverified. |
| UR Academy certificate — 5% | Not part of this project | Completion unverified. |
| Attendance, participation, peer feedback — 10% | Not part of this project | Completion unverified. |

The three simulation formats exist. That does not establish completion of the entire assignment or guarantee a particular mark. Physical collision checks, joint speed/acceleration limits, contact mechanics, calibrated tooling and safe hardware execution are outside the completed work.

## MIDI addition

`MIDI-Drum-Robots.gh` is an optional reusable extension. Imported MIDI bytes are internalized automatically; save after import. The original demo was validated and reloaded without an external MIDI path. GM note mappings are editable. Toms may be explicitly routed to snare or ignored; unmatched notes are reported. MIDI audio synthesis and unrestricted percussion-to-robot scheduling are not implemented.
