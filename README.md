# Birdland: four robot arms

Rhino 8 + Grasshopper + Robots 2.4.0 study: two stick arms, a kick-pedal arm and a hi-hat-pedal arm. Includes a reusable, internally cached Standard MIDI drum importer.

Read [how AI helped build the demo](docs/ai-assisted-development.md) for the MCP/Rhino control architecture, music analysis, Grasshopper implementation and validation.

## Open the project

1. Install Rhino 8 with its Python 3 scripting support, Robots 2.4.0, and the UniversalRobot library. Put `UniversalRobot.xml` and `UniversalRobot.3dm` in `~/Documents/Robots`; Rhino package-version folders may be cleaned during startup.
2. Open a blank Rhino document, then `grasshopper/Birdland-Python3.gh` for the recorded Birdland choreography, or `grasshopper/MIDI-Drum-Python3.gh` for the reusable MIDI adapter. The definitions contain their stage geometry and Python source.
3. Drag `PLAYBACK / 0 to 1` to scrub. The `.gh` does not play or synthesize audio. The Birdland MP4 uses the original recording.
4. `assets/Birdland-Robots.3dm` is an optional baked scene with materials and lights. Opening it while GH previews are visible duplicates the geometry.

## Grasshopper component flow

The recommended definitions expose four separate lanes: hit times → rebound → target plane → native Robots Create Target → native Robots Kinematics → preview. Robot model, mounting planes and tool lengths are visible inputs. Each solver exposes joint angles, joint planes and IK errors. Pedal linkages use the same lift values as their arms.

Small **Rhino 8 Python 3** components handle event parsing, articulation and geometry. All script source, event data and stage geometry remain embedded; no extra Python packages are required. The robot loaders, tools, target builders and kinematics solvers are native Robots components. See [the component map](docs/components.md).

The recommended `*-Python3.gh` files contain no legacy GhPython components or OLD badges. The previous `*-Components.gh` and original monolithic `*-Robots.gh` definitions remain as regression baselines. The existing movie renderer still uses the monolithic baseline; migration does not change the rendered performance.

## Import a drum MIDI

In `MIDI-Drum-Python3.gh`, paste an absolute `.mid`/`.midi` path into `MIDI / FILE TO IMPORT`. A successful import copies the original bytes into `MIDI / EMBEDDED BYTES` and clears the external path. **Save the GH file after import.** It then works without the source MIDI file. An original 9-second demo is embedded and also provided in `examples/demo-drums.mid`.

- Standard MIDI types 0 and 1, tempo maps, running status and SMPTE timing are supported. Type 2 independent sequences and MIDI 2.0 clip files are not supported.
- Channel 0 selects GM channel 10, or the sole mapped channel. Select 1–16 explicitly when an auto choice is ambiguous; -1 imports all channels.
- Edit the note map for non-GM drum layouts. It supports kick, snare, rim, hats, hat pedal, crash/ride and optional tom-to-snare routing.
- Unknown notes and tom approximations are reported. Velocity controls rebound height. Open/closed hi-hat notes drive pedal state.
- Two stick arms cannot faithfully reproduce every dense or simultaneous percussion arrangement. This is a kinematic adaptation, not a universal drum-performance compiler or controller program.

## Video and assignment status

The current director edit uses an orbital view alternating with moving drum close-ups, 3D fireworks aligned to measured ensemble onsets, and brief rim-contact highlights. Native capture: 3840×2160 at 24 fps; output: 70 seconds, with audio and picture fading from 65 to 70 seconds. Rendering/finishing code is separate from the internally referenced GH robot definition.

See `docs/assignment-audit.md` for exact deliverables and gaps. `docs/Birdland-Pseudocode.pdf` contains the diagram and one paragraph of design intent. Generated movies, frame sequences, original third-party music and separated stems are local build artifacts and are not committed. Their location is recorded in `docs/local-artifacts.md`.

## Checks

Run `python3 -m unittest discover -s tests -v`. Parser tests cover tempo-map timing, running status, channel ambiguity, SMPTE, mapping, note-on velocity zero, malformed data and unsupported formats. Native GH validation reports are in `data/`: the embedded MIDI demo was sampled at 217 instants (868 arm poses), and the saved file reloaded with 49 output meshes and no import/solver errors.

The Python 3 definitions were checked at 57 playback positions each: 456 arm poses, 49 meshes per sample, zero IK errors and identical mesh-vertex hashes compared with the originals. Both saved definitions reloaded successfully. A fresh MIDI import also survived save/reload with its source file removed; a malformed import reported an error, preserved the valid cache and recovered after clearing the bad path. Reports are in `data/python3-*.json`.

No physical robot connection, toolpath execution, collision validation or dynamic certification has occurred.

## Sources

- Audio: Weather Report official artist channel, https://www.youtube.com/watch?v=SvhmaNlLgRM
- Drum chart: Pedro Marambio / Drumeo, https://d1923uyy6spedc.cloudfront.net/weather-report-birdland-1674639029.pdf
- Robots plugin: https://github.com/visose/Robots
- MIDI standard: https://midi.org/standard-midi-files
