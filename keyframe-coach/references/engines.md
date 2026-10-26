# Export targets

Shared rules: one Action per clip, named the way the engine will show it. Apply object scale and rotation to the armature before the first export. Keep only deform bones in the exported skeleton (control rig bones stay in Blender). Re-import the exported file into a fresh Blender scene to check it.

## Unity

- Format: FBX (File > Export > FBX).
- Settings: Apply Scalings "FBX Units Scale"; Forward -Z, Up Y; Armature: **Add Leaf Bones off**, "Only Deform Bones" on when a control rig is used; Bake Animation on; turn on "All Actions" or "NLA Strips" to export every clip.
- Rig type: **Humanoid** retargets between characters but ignores most bone scale and twist bones, so no squash & stretch. **Generic** keeps everything.
- Root motion: set in the clip import settings (Root Transform Rotation/Position "Bake Into Pose" for in-place parts).
- Loops: tick Loop Time on the clip. Unity treats the last frame as equal to the first, so key the end frame identical to the start.
- fps: anything; 30 is usual.

## Unreal

- Format: FBX.
- Scale: Unreal uses centimetres. Either set Scene Units to Metric, Unit Scale 0.01 before rigging, or keep 1.0 and use FBX "Apply Scalings: FBX Units Scale". Pick one and keep it for every file.
- If the armature object is named exactly `Armature`, Unreal drops it as an extra root node; any other name becomes an extra root bone.
- Root motion: needs a single top bone (usually `root`) at the origin carrying the travel; enable Root Motion on the Anim Sequence.
- Bone scale is supported, so squash & stretch works.
- Settings: Add Leaf Bones off, Bake Animation on, "Only Deform Bones" with a control rig.
- Loops: matching first and last frames; set looping on the sequence or in the state machine.
- fps: 30 by default; the import can resample.

## Godot (4.x)

- Format: glTF 2.0 binary (`.glb`). Godot can also import `.blend` directly if the Blender path is set in its editor settings.
- glTF settings: Animation mode "Actions" (each action becomes an animation); Sampling on; "Export Deformation Bones Only" with a control rig.
- Loops: an action whose name ends in `-loop` or `_loop` imports as looping. Otherwise set it in the Advanced Import Settings.
- Root motion: set `AnimationTree.root_motion_track` to the root bone.
- Bone scale is supported.

## Roblox

- For R6 rigs, use the `roblox-blender-setup` skill (rig, IK control rig, Rbx Animations bake/export). For R15 or custom skinned rigs, export FBX and import it in the Studio Animation Editor; verify that path with the user, since it has not been tested here.
- **No bone scale animation**: Motor6D and bone rigs ignore it, so no squash & stretch. Sell impacts with poses and timing.
- Rig units are studs; the R6 rig is about 5 units tall.
- Looping and priority (Core, Idle, Movement, Action) are set on the animation in Studio, not in Blender.
- Keys are stored in seconds, so any Blender fps works; 30 or 60 match the editor's snapping.
