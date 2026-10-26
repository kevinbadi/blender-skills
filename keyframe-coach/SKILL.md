---
name: keyframe-coach
description: Animate game characters and props in Blender using the 12 principles of animation adapted for games (responsiveness, loops, blending, root motion, export). Use when the user wants to animate, block, polish, review or export a character/creature/weapon animation in Blender for a game engine (Unity, Unreal, Godot, Roblox), or asks why an animation looks stiff, floaty, slidey or pops in-engine.
---

# Keyframe Coach

`SKILL_DIR` = the directory containing this file.

## Connector: MCP for Blender (official)

All Blender work goes through the official **MCP for Blender** server (tools `mcp__blender__*`). If they are deferred, load them in one ToolSearch call: `select:mcp__blender__get_addon_status,mcp__blender__get_scene_info,mcp__blender__execute_blender_code,mcp__blender__look`.

- Start with `get_addon_status`. "Could not connect" means Blender is not running or the add-on's server is off. Don't launch or repair it yourself: work headless (below). If the user wants to watch in a live Blender, tell them to enable **Interface: MCP for Blender** in Preferences → Add-ons and click **Start MCP Server**.
- If it reports `up_to_date: false` but connects, carry on and mention `uvx mcp-for-blender install-addon` to the user.
- `get_scene_info`: scene facts as text. Use `fields: ["animation", "details"]` for actions and bones, `fields: ["settings"]` for frame range and fps, `root`/`query` to find the armature.
- `execute_blender_code`: runs bpy in the live Blender. Print what you need; work in small steps.
- `look`: the only way to see the result (see Workflow step 7).
- Do not use the old third-party `blender-mcp` (ahujasid) tools such as `get_viewport_screenshot` or `get_object_info`.

## Headless and keeping runs cheap

Every turn re-reads the whole conversation, so the number of turns and of images drives the cost.

- Without the connector, keep the whole animation in one script file and make each pass a single command: rebuild, audit and, when needed, render: `blender -b -P anim.py -- out.blend && blender -b out.blend --python-expr "exec(open('<SKILL_DIR>/scripts/audit.py').read()); audit(...)"`.
- Change that script with the Edit tool, not `sed`: line edits in Python break indentation and cost a turn each time.
- Each image stays in context for the rest of the session. Look only once the audit is clean, and tile the key frames into one contact sheet per view (≤1024 px wide) instead of separate images: `ffmpeg -pattern_type glob -i 'f_*.png' -vf "scale=256:-1,tile=4x2" -frames:v 1 sheet.png`. Look again only after a visible change.
- Don't read `audit.py`: each line it prints says what it measured and by how much.

## Step 0: two mandatory questions (always, before any animation work)

Ask both with the AskUserQuestion tool in one call. Skip a question only if the user already answered it in this conversation. Do not guess or assume defaults.

1. **Export target**: Unity, Unreal, Godot, Roblox (Other → ask which).
2. **Style**: Realistic, Stylized/cartoony, Blocky/rigid-part (Roblox-like, low-poly), Anime/snappy.

Then read `references/engines.md` (the target's section only) and the matching style row in `references/principles.md`. For Roblox R6 rigs, also load the `roblox-blender-setup` skill and follow it for the rig and export steps. For a creature with more than two legs, also read `references/legs.md`.

Ask these too when they matter and are not obvious from the request: is the clip a **loop** (walk, run, idle) or a **one-shot** (attack, jump)? **In-place or root motion**? Is it **player-triggered** (needs fast startup) or **AI/cinematic**? For more than two legs: which **gait** (walk, trot, gallop; creep or scuttle for insects and spiders)?

## Workflow

1. **Inspect**: `mcp__blender__get_addon_status`, then `mcp__blender__get_scene_info` (with `fields: ["animation", "details", "settings"]`), then find the armature, its actions, the frame range and fps. Headless: print all of that, plus each leg's lowest bone, from one script.
2. **Plan timing**: write down the key poses and the frame number of each before keying. For attacks, list startup, active and recovery frames. Use `references/principles.md` for frame counts.
3. **Block** (pose-to-pose): key only the main poses, all on the same frames, with stepped/constant interpolation so the timing reads.
4. **Breakdowns**: add in-betweens that put the limbs on arcs. Check with Motion Paths.
5. **Spline and polish**: switch to Bezier, then offset the overlapping parts (head, arms, tail, cloth) by 1–3 frames, add overshoot and settle, and fix the easing.
6. **Audit**: run `scripts/audit.py` (below) and fix what it reports.
7. **Look**: `mcp__blender__look` with `mode: "frames"` and `frames: [...]` on the key frames, once with `view: [1, 0, 0.1]` (side) and once with `view: "camera"` (gameplay angle). Use `shading: "xray"` to see bones and `max_size: 512` for quick checks. Headless: one contact sheet per view (above).
8. **Export** using the target's settings in `references/engines.md`.

Blender 5.x: `action.fcurves` is gone. Read curves through `bpy_extras.anim_utils.action_get_channelbag_for_slot(action, obj.animation_data.action_slot)`.

## Audit

`scripts/audit.py` reads the animation data and reports concrete problems: loop seams that don't match, foot sliding, feet clipping through the floor, leftover linear keys, scale keys the engine will drop, every bone keyed on the same frames (no overlap), and left/right twinning. It changes nothing. Run it with `mcp__blender__execute_blender_code`, or headless as above (never skip it):

```python
exec(open("<SKILL_DIR>/scripts/audit.py").read())
audit("Armature", engine="unity", loop=True, feet=["foot.L", "foot.R"])
```

Pass `feet` as the lowest bone of every leg, all of them (front paws are often named hand or wrist); the foot checks are skipped without it. Treat its output as hints, not verdicts: a linear key on a mechanical motion or a held pose on purpose is fine. Tell the user what it found and what you will change before changing it.
