# Read-only audit of an armature's active action. Usage (inside Blender):
#   exec(open(".../audit.py").read()); audit("Armature", engine="unity", loop=True)
import bpy, re, statistics

NO_SCALE = {"roblox"}  # targets that drop bone scale keys (Unity Humanoid too; warned separately)


def _fcurves(obj):
    ad = obj.animation_data
    act = ad.action
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        return act, (list(cb.fcurves) if cb else [])
    except (ImportError, AttributeError):  # Blender < 4.4
        return act, list(act.fcurves)


def _bone(fc):
    m = re.match(r'pose\.bones\["(.+?)"\]', fc.data_path)
    return m.group(1) if m else None


def _mirror(name):
    for a, b in ((".L", ".R"), ("_L", "_R"), ("_l", "_r"), ("Left", "Right"), ("left", "right")):
        if a in name:
            return name.replace(a, b)
    return None


def audit(arm_name, engine="", loop=None, feet=None, in_place=None, eps=1e-3):
    obj = bpy.data.objects[arm_name]
    scene = bpy.context.scene
    if not (obj.animation_data and obj.animation_data.action):
        print(f"{arm_name}: no active action"); return
    act, fcs = _fcurves(obj)
    # manual range if set, else the keyed range (a loop keyed 1-17 with 17 = 1 renders 1-16)
    f0, f1 = (int(f) for f in act.frame_range)
    engine = engine.lower()
    out = [f"Audit '{act.name}' on {arm_name}: frames {f0}-{f1} @ {scene.render.fps} fps, {len(fcs)} curves"]

    # Loop seams: end value must equal start; on hand-keyed Bezier curves the end handles must match too.
    # shortcut: sampled curves (keys every 1-2 frames) carry the motion's own kinks, e.g. a paw landing on frame 1, so
    # their tangents aren't judged; compare evaluated slopes against a cyclic fit if scripted seam hitches slip through
    if loop:
        bad = set()
        for fc in fcs:
            kp = fc.keyframe_points
            hitch = False
            if (len(kp) > 1 and kp[0].co.x == f0 and kp[-1].co.x == f1 and kp[0].interpolation == "BEZIER"
                    and (f1 - f0) / (len(kp) - 1) > 2):
                a, z = kp[0], kp[-1]
                s0 = (a.handle_right.y - a.co.y) / max(1e-6, a.handle_right.x - a.co.x)
                s1 = (z.co.y - z.handle_left.y) / max(1e-6, z.co.x - z.handle_left.x)
                # speed the loop should carry through the seam, from the keys either side of it
                through = (kp[1].co.y - kp[-2].co.y) / (kp[1].co.x - kp[-2].co.x + f1 - f0)
                hitch = (abs(s0 - s1) > max(eps, 0.25 * max(abs(s0), abs(s1)))  # jumps speed at the seam
                         or max(abs(s0), abs(s1)) < 0.25 * abs(through) - eps)  # eases to a stop mid-motion
            if abs(fc.evaluate(f0) - fc.evaluate(f1)) > eps or hitch:
                bad.add(_bone(fc) or fc.data_path)
        if bad:
            out.append(f"LOOP SEAM: start/end value or speed don't match (a Cycles F-curve modifier fixes end handles) on {', '.join(sorted(bad)[:8])}")

    # Interpolation leftovers
    lin = sum(1 for fc in fcs for k in fc.keyframe_points if k.interpolation in {"LINEAR", "CONSTANT"})
    if lin:
        out.append(f"INTERPOLATION: {lin} linear/constant keys (fine if blocking or mechanical, otherwise ease them)")

    # Quaternion keys in opposite hemispheres make Blender blend the long way (limb snaps through rest)
    quats = {}
    for fc in fcs:
        if fc.data_path.endswith("rotation_quaternion"):
            quats.setdefault(fc.data_path, {})[fc.array_index] = fc
    flips = []
    for path, g in quats.items():
        if len(g) < 4:
            continue
        frames = sorted({k.co[0] for k in g[0].keyframe_points})
        qs = [[g[i].evaluate(f) for i in range(4)] for f in frames]
        if any(sum(a * b for a, b in zip(p, q)) < 0 for p, q in zip(qs, qs[1:])):
            flips.append(_bone(g[0]) or path)
    if flips:
        out.append(f"QUATERNION FLIP (limb swings the long way between keys; negate the later key): {', '.join(flips[:8])}")

    # Scale animation the target may drop
    scaled = sorted({_bone(fc) or fc.data_path for fc in fcs if fc.data_path.endswith("scale")
                     and len({round(k.co[1], 4) for k in fc.keyframe_points}) > 1})
    if scaled:
        tag = "WILL BE DROPPED" if engine in NO_SCALE else ("dropped by Unity Humanoid rigs" if engine == "unity" else "ok")
        out.append(f"SCALE KEYS ({tag}): {', '.join(scaled[:8])}")

    # Overlap / twinning: compare which frames each bone is keyed on
    keyset = {}
    for fc in fcs:
        b = _bone(fc)
        if b:
            keyset.setdefault(b, set()).update(round(k.co[0]) for k in fc.keyframe_points)
    multi = {b: s for b, s in keyset.items() if len(s) > 2}
    # shortcut: key timing says nothing about baked or scripted clips (keys every 1-2 frames); measure motion timing if those need these checks
    if multi and max(b - a for s in multi.values() for a, b in zip(sorted(s), sorted(s)[1:])) <= 2:
        out.append("OVERLAP/TWINNING not checked: keys every 1-2 frames (baked or scripted)")
        multi = {}
    if len(multi) > 2 and len({frozenset(s) for s in multi.values()}) == 1:
        out.append("NO OVERLAP: every animated bone is keyed on the same frames; offset follow-through parts 1-3 frames")
    twins = [b for b in multi if _mirror(b) in multi and b < _mirror(b) and multi[b] == multi[_mirror(b)]]
    if twins:
        out.append(f"POSSIBLE TWINNING (L/R keyed on identical frames): {', '.join(twins[:8])}")

    # Constraints the engine won't evaluate
    cons = [pb.name for pb in obj.pose.bones if any(c.enabled and c.influence > 0 for c in pb.constraints)]
    if cons and engine:
        out.append(f"CONSTRAINTS on {len(cons)} bones: make sure export bakes animation (Bake Animation / glTF sampling)")

    # Foot contact: planted feet should be still (root motion) or move at constant speed (in-place)
    if feet:
        mw = obj.matrix_world
        zs = [(mw @ v).z for b in obj.data.bones for v in (b.head_local, b.tail_local)]
        height = max(1e-6, max(zs) - min(zs))
        # the foot's sole = skinned vertices that follow that bone most (bone ends miss toes the rig has no bone for)
        skins = [m for m in scene.objects if m.type == "MESH" and m.find_armature() == obj]
        soles = {n: [(m, [v.index for v in m.data.vertices if v.groups and
                          m.vertex_groups[max(v.groups, key=lambda g: g.weight).group].name == n]) for m in skins] for n in feet}
        cur = scene.frame_current
        track = {n: [] for n in feet}  # per frame: (head, tail) in world space
        low = {n: [] for n in feet}  # per frame: lowest point of the foot (sole, else bone end)
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            zs = {}
            for m in skins:
                ev = m.evaluated_get(dg)
                zs[m] = [(ev.matrix_world @ v.co).z for v in ev.to_mesh().vertices]
                ev.to_mesh_clear()
            for n in feet:
                pb = obj.pose.bones[n]
                track[n].append((mw @ pb.head, mw @ pb.tail))
                sole = [zs[m][i] for m, idx in soles[n] for i in idx]
                low[n].append(min(sole) if sole else min(q.z for q in track[n][-1]))
        scene.frame_set(cur)
        src = {n: "skinned mesh" if any(idx for _, idx in soles[n]) else "bone ends" for n in feet}
        for n in feet:  # gap given so each leg can be corrected straight from this line
            gap = min(low[n]) - mw.translation.z
            if gap > 0.03 * height:
                out.append(f"FOOT NOT ON FLOOR ({n}): lowest point ({src[n]}) stays {gap:.3f} above the floor (armature origin); "
                           "it hovers, or isn't a foot bone")
                del track[n]
        if in_place is None and track:
            in_place = max((ps[-1][0] - ps[0][0]).to_2d().length for ps in track.values()) < 0.1 * height
        for n, ps in track.items():
            # planted point = whichever end (heel or toe) stays on the floor; its ground travel is the slide,
            # so a heel-toe roll reads still while a foot sliding flat on the floor still counts
            # game rigs keep the armature origin on the floor
            dip = mw.translation.z - min(low[n])
            if dip > 0.03 * height:
                out.append(f"FOOT BELOW FLOOR ({n}): lowest point ({src[n]}) {dip:.3f} under the floor (armature origin) at frame "
                           f"{f0 + low[n].index(min(low[n]))}; it clips through (often a swing leg that doesn't fold enough)")
            floor = min(q.z for p in ps for q in p)
            speeds = []
            for a, b in zip(ps, ps[1:]):
                moves = [(b[i] - a[i]).to_2d().length for i in (0, 1)
                         if max(a[i].z, b[i].z) - floor < 0.03 * height]
                if moves:
                    speeds.append(min(moves))
            if len(speeds) < 2:
                continue
            if in_place:
                mean = statistics.mean(speeds)
                if mean > 1e-3 * height and statistics.pstdev(speeds) / mean > 0.3:  # still feet are fine
                    out.append(f"FOOT SLIDE ({n}): contact speed uneven ({min(speeds):.3f}-{max(speeds):.3f}/frame); in-place feet should slide at constant speed")
            elif sum(speeds) > 0.02 * height:
                out.append(f"FOOT SLIDE ({n}): planted foot drifts {sum(speeds):.3f} units during contact")
        out.append(f"FEET checked: {', '.join(track) or 'none'} ({'in-place' if in_place else 'root motion'})")
    else:
        out.append("FEET: not checked; pass feet=[the lowest bone of every leg]")

    if len(out) == 1:
        out.append("No issues found.")
    print("\n".join(out))
    return out
