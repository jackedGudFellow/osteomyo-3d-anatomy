# Skeleton rebuild (BodyParts3D v3.0)

The app source is not in this repo, so the skeleton was rebuilt by converting meshes and patching the built bundles.

1. `mapping.py` maps each of the app's bone ids to BodyParts3D FMA ids (sternum = manubrium + body + xiphoid; ribs 1-7 include their costal cartilage).
2. `fetch.py` pulls the STL files from https://github.com/Kevin-Mattheus-Moerman/BodyParts3D (mirror of BodyParts3D v3.0).
3. `convert.py` converts z-up mm STL to the app's `O3DB` format (y-up metres, centred on bbox, decimated, gzip).
4. `fit_layout.py` places each bone at its true position with one uniform scale (the original layout was ~1.5x too narrow for its height).
5. `patch.py` injects the layout into the data bundles, warps organ/nerve/shell positions to match, and renames the bundles (new content hashes).

Scripts expect their inputs under `/tmp/work` and `/tmp/bp3d`; edit the paths if you rerun them. Re-running `patch.py` needs the original bundles (`git show 2169daa:assets/...`).
Models: BodyParts3D, (c) The Database Center for Life Science, CC Attribution-Share Alike 2.1 Japan.
