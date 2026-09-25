# Rebuild the director edit

1. Open `assets/Birdland-Robots.3dm` in Rhino 8, and launch Grasshopper once. Run `src/initialize_scene.py` with `_-RunPythonScript`. This loads the internally referenced Birdland GH and reconnects the baked dynamic objects.
2. Set the start/end frame range in `data/render-batch.json`. End is exclusive; complete output requires 0 through 1679. Start with 0..240, then 240..480, etc.
3. Run `src/render_director.py` in Rhino for each batch. It captures native 3840×2160 PNGs under `renders/director4k/frames/` and writes a per-batch validation report. The source animation's 75-second clock is retained; the movie uses its first 70 seconds.
4. Run `src/make_overlay.py` with Pillow, then `src/encode.sh` with ffmpeg after all 1680 frames exist. Supply the original recording as `assets/audio/opening-75.wav` first. The script checks the frame count before encoding.

Camera cuts, analyzed shot timestamps and strengths are in `data/edit-analysis.json`. Fireworks are built in world coordinates by a Rhino display conduit. The camera and effects are presentation code; the GH definition handles the robot motion and stage.

Long Rhino viewport exports can retain considerable memory. Use short batches, preserve every completed frame, and restart Rhino between batches if necessary; then rerun initialization. Do not close a session containing other unsaved user work. The exporter writes per-batch validation, but does not claim collision or dynamic certification.

To reanalyze audio, place `opening-75.wav` and `analysis/htdemucs/opening-75/drums.wav` under `assets/audio/`, then run `src/analyze_audio.py` with numpy, scipy, soundfile and matplotlib. The analysis uses positive spectral-energy changes in the separated drum stem and original mix. Treat its instrument labels and inferred choreography as approximate.

The revised opening uses hi-hat at 17.9167–20 seconds, then hi-hat pedal at 20–22.125 seconds. It removes the two early kick close-ups based on listening feedback. Other instrument mappings remain approximate. Capture now primes the output dimensions before setting the first camera to avoid a one-frame projection mismatch; the reported glitch at frame 960 was re-rendered and checked against frames 959 and 961.

`render-batch.json` may include an explicit `frames` array for targeted fixes. `BIRDLAND_OUTPUT` overrides the capture directory. `encode.sh` accepts `BIRDLAND_FRAMES`, `BIRDLAND_AUDIO`, `BIRDLAND_OUTPUT` and `BIRDLAND_OVERLAY`.
