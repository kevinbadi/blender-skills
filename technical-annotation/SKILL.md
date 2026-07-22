---
name: technical-annotation
description: Annotate a 3D scene with force vectors, angle arcs, and value labels for technical explainer and engineering videos. Orthographic camera keeps angles undistorted. Trigger when the user wants a physics/statics diagram, force arrows, an angle sweep, dimension callouts, or an animated technical explainer rather than a product beauty shot.
---

## Technical Annotation

Turns a plain 3D scene into a readable **technical diagram in motion**: force vectors that scale with a value, an angle arc that sweeps, and text labels that update per frame. Uses an **orthographic** camera so angles and proportions stay true — the thing product-showcase skills can't give you, because perspective distorts the very quantity you're trying to teach.

Unlike the other skills in this repo, the goal here is not to make an object look beautiful — it's to make a *quantity* legible: a lashing angle, a lever arm, a load path, a clearance.

## When to Use

- User wants an engineering / physics / statics explainer ("show how the force changes with the angle")
- User says "force arrow", "vector", "angle arc", "dimension line", "callout", "free-body diagram"
- Any animation where a **number drives the visuals** (arrow length ∝ force, arc ∝ angle)
- NOT for product beauty shots — use turntable / slow-zoom for those

## Prerequisites

- **Blender MCP**: Connected (or run the same `bpy` code headless with `blender -b -P`)
- **Scene**: the object(s) you're annotating are already in the scene
- **ffmpeg**: Installed for video encoding
- **Output folder**: `~/Desktop/Blender Videos/`

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duration` | `6` | Video length in seconds |
| `fps` | `25` | Frames per second |
| `ortho_scale` | `10` | Orthographic view size (larger = more zoomed out) |
| `accent_hex` | `#1E88E5` | Colour for arrows / arcs / active labels |
| `label_hex` | `#222222` | Colour for static text |
| `arrow_max_len` | `2.0` | Length of a force arrow at 100% magnitude |
| `driver` | — | The value that drives the animation (e.g. angle in degrees) |

## Flow

### Step 1: Lock the camera to orthographic

Angles read truthfully only without perspective. Point the camera straight down −Y so the XZ plane is the drawing surface.

```python
import bpy, math

cam_data = bpy.data.cameras.new("OrthoCam")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 10          # ortho_scale
cam = bpy.data.objects.new("OrthoCam", cam_data)
cam.location = (0, -14, 1.3)
cam.rotation_euler = (math.radians(90), 0, 0)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

# Accurate colour: the default AgX view transform desaturates flat graphics.
bpy.context.scene.view_settings.view_transform = 'Standard'
```

### Step 2: Emission materials for labels and arrows

Annotations must stay the exact spec colour and stay legible regardless of lighting — so make them emissive, not lit.

```python
def pure_color(name, hex_str):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    def s2l(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    h = hex_str.lstrip('#')
    rgb = [s2l(int(h[i:i+2],16)/255) for i in (0,2,4)]
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emit = nt.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (*rgb, 1)
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat
```

### Step 3: Build the annotation primitives

A force **arrow** (shaft cylinder + cone head), an **angle arc**, and a **text label**. All live in the XZ plane so they face the orthographic camera.

```python
from mathutils import Vector

def cylinder(p1, p2, r, mat, name):
    v1, v2 = Vector(p1), Vector(p2); d = v2 - v1
    if d.length < 1e-6: return None
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length,
                                        location=(v1+v2)/2, vertices=16)
    o = bpy.context.object; o.name = name
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.to_track_quat('Z', 'Y')
    o.data.materials.append(mat); return o

def arrow(start, direction, length, mat, name, r=0.045):
    d = Vector(direction).normalized(); s = Vector(start)
    head = min(0.22, length*0.35); shaft_end = s + d*(length-head)
    cylinder(s, shaft_end, r, mat, name+'_shaft')
    bpy.ops.mesh.primitive_cone_add(radius1=r*2.4, depth=head,
                                    location=shaft_end + d*(head/2), vertices=16)
    c = bpy.context.object; c.name = name+'_head'
    c.rotation_mode = 'QUATERNION'
    c.rotation_quaternion = d.to_track_quat('Z', 'Y')
    c.data.materials.append(mat)

def label(text, loc, size, mat, align='LEFT'):
    cu = bpy.data.curves.new('t', type='FONT')
    cu.body = text; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('label', cu)
    o.location = loc; o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat)
    bpy.context.collection.objects.link(o); return o
```

### Step 4: Render frame-by-frame so a value can drive the scene

Text bodies and arrow lengths aren't keyframable in a natural way, so drive them in a Python loop instead of `render(animation=True)`. Rebuild the dynamic parts each frame; **cache materials by name and purge orphans** or every frame gets slower.

```python
import os
accent = pure_color('accent', '#1E88E5')
scene = bpy.context.scene
TOTAL = DURATION * FPS
out = os.path.expanduser('~/Desktop/Blender Videos/annot_frames')
os.makedirs(out, exist_ok=True)

def value_at(f):                      # example driver: angle 90° -> 20°
    t = (f-1)/(TOTAL-1); return 90 + (20-90)*t

for f in range(1, TOTAL+1):
    for o in [o for o in bpy.data.objects if o.name.startswith('DYN')]:
        bpy.data.objects.remove(o, do_unlink=True)
    ang = value_at(f)
    mag = math.sin(math.radians(ang))          # the quantity being taught
    arrow((0, -0.2, 1.4 + mag*ARROW_MAX_LEN), (0,0,-1),
          0.3 + mag*ARROW_MAX_LEN, accent, 'DYNarrow')
    label(f"{ang:.0f} deg   ->   {mag*100:.0f} %", (1.2, 0, 3.4), 0.3, accent)
    bpy.data.orphans_purge(do_local_ids=True, do_recursive=True)
    scene.frame_set(f)
    scene.render.filepath = os.path.join(out, f"{f:04d}")
    bpy.ops.render.render(write_still=True)
```

### Step 5: Encode

```bash
ffmpeg -y -framerate 25 \
  -i "~/Desktop/Blender Videos/annot_frames/%04d.png" \
  -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le \
  "~/Desktop/Blender Videos/technical_annotation.mov"
```

## Tips

- **Orthographic is non-negotiable for angles.** In a perspective view the same angle looks different depending on where it sits in frame — which defeats a technical explainer.
- **Watch the font.** Many fonts (Poppins, most geometric sans) have no Greek glyphs — α and μ render as an empty box. Verify with a one-frame test, and fall back to a font with Greek coverage (Arial, DejaVu Sans) for those strings. This is a silent failure: no error, just a blank box.
- **Drive visuals from the real number.** Arrow length ∝ value, arc ∝ angle. If the scene pulls from a verified calculation, the animation can't drift from the maths.
- **`view_transform = 'Standard'`** for flat diagram colour; the default AgX tone-maps and desaturates your accent colour. (Keep AgX for photoreal product shots — this is the opposite case.)
- **Colour = state.** Turn the accent red/amber/green as the value crosses thresholds; the viewer reads the verdict before reading the number.
- For a rotating callout or an orbit around the annotated object, parent the camera to a pivot empty and animate the **pivot's rotation** — never two location keyframes, or the camera cuts a straight chord through the object.
