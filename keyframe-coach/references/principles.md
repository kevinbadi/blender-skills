# The 12 principles, adapted for game animation in Blender

Frame counts assume 30 fps. Scale them for other rates (×2 at 60 fps, ×0.8 at 24 fps).

## Style dials

| Style | Exaggeration | Squash & stretch | Overshoot | Timing feel |
|---|---|---|---|---|
| Realistic | Low (10–20% past natural) | None | Small, 2–4 frame settle | Smooth Bezier, few holds |
| Stylized/cartoony | High (30–60%) | Yes, if the engine keeps bone scale | Big, 4–8 frame settle | Snappy accelerations, short holds on key poses |
| Blocky/rigid-part | Medium–high; sell it with poses | None (rigid parts) | Medium | Snappy; moves read well on twos |
| Anime/snappy | High in the poses, low in between | Rare, on impact frames only | Small | Fast transitions into long holds; smear-like 1-frame stretched poses |

## Principles

**1. Timing.** Count frames, don't eyeball them. Rough budgets (30 fps):
- Walk cycle: 30–36 frames for 2 steps. Run: 16–22. Idle loop: 60–120.
- Player light attack: startup 2–5, active 2–4, recovery 8–15. Heavy: startup 8–15.
- Jump: crouch 3–4, rise and fall driven by gameplay, land 4–8.
Mark the contact and hit frames with timeline markers so gameplay code can use them.

**2. Slow in / slow out.** Ease into and out of the key poses (Bezier, Graph Editor). Exceptions: loop seams need matching tangents on both ends, and a strike is fastest just before contact, with no ease there.

**3. Arcs.** Hands, feet, head and weapon tips travel on arcs. Turn on Motion Paths (Pose > Motion Paths) for the IK controls and fix kinks with breakdown keys. A straight path between two keys means a breakdown is missing.

**4. Anticipation.** Player-triggered actions get 1–3 frames, or none, because every frame of wind-up is input lag. Put the weight into the follow-through instead. Enemy and AI attacks get long, readable telegraphs (10–30 frames), since that is how the player knows to dodge.

**5. Follow-through and overlapping action.** The parts that follow (head, off-arm, hair, tail, cloth, weapon) lag the root motion by 1–3 frames and settle after it stops. Offset their keys in the Dope Sheet. Decide whether the engine's physics (jiggle or spring bones, cloth) handles hair and cloth; if so, don't key them as well.

**6. Secondary action.** Breathing, blinks, finger curls, a weight shift in the idle. It must support the main action, not compete with it, and it must loop cleanly.

**7. Straight ahead vs pose-to-pose.** Use pose-to-pose: block the key poses, then breakdowns, then splines. Straight-ahead makes loops and later edits painful. Only use it for chaotic secondary parts, and prefer engine physics for those.

**8. Exaggeration.** Game characters are seen small, fast and from a distance. Push the key poses past what looks right in the Blender viewport, then check them from the gameplay camera.

**9. Solid drawing → weight, balance and silhouette.** Keep the centre of mass over the support foot. Avoid twinning: left and right limbs mirrored on the same frames. Check that every key pose reads as a silhouette (flat shading, black material).

**10. Appeal.** Clear poses, readable intent, personality that fits the character. Make it the final review pass: would a player know what this character is doing, and how it feels, from one frame?

**11. Squash and stretch.** Only for the stylized style, and only if the target keeps bone scale (see engines.md). Preserve volume: when one axis stretches, the other two shrink.

**12. Staging.** In gameplay the player controls the camera, so a pose must read from any angle, mostly from behind and above. Classic staging still fully applies to cutscenes and emotes.

## Game-only rules (not in the 12)

- **Loops**: the last frame equals the first, or the clip ends one frame before a repeat of the first (match the engine's convention, see engines.md). Use the Cycles F-curve modifier while working so the seam is visible.
- **Root motion vs in-place**: in-place means feet slide backward at a constant ground speed during contact. Root motion means the root bone carries the travel and planted feet stay fixed in world space. Pick one per project.
- **Blendability**: start and end near the idle or neutral pose, keep the root height and facing consistent between clips, and avoid pose flips (keep quaternions in the same hemisphere).
- **Contact**: planted feet don't slide, or slide uniformly for in-place loops. Hands on props stay locked (use IK or Child Of with keyed influence).
- **Bake**: engines don't evaluate Blender constraints or drivers. Export bakes them; check the result after export.
