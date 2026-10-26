# More than two legs

Read this for quadrupeds, insects, spiders and other many-legged creatures. Everything in principles.md still applies to each leg; what changes is the stepping order and how many feet carry the body.

## Gaits

Phase is the moment each foot plants, as a fraction of one cycle. Stance is the fraction of the cycle a foot spends on the ground. Legs are numbered front to back (L1 = left front).

| Creature, gait | Feet plant at (phase) | Feet down | Stance |
|---|---|---|---|
| Quadruped walk | LH 0, LF 0.25, RH 0.5, RF 0.75 | 2–3 | 60–70% |
| Quadruped trot | LH+RF 0, RH+LF 0.5 (diagonal pairs) | 2 | 40–50% |
| Quadruped canter/gallop | Hind pair, then fore pair, each pair slightly split; one airborne phase | 0–3 | 20–35% |
| Insect (6), alternating tripod | L1+R2+L3 0, R1+L2+R3 0.5 | 3 | ~50% (more when slow) |
| Spider (8), alternating tetrapod | L1+R2+L3+R4 0, R1+L2+R3+L4 0.5 | 4 | ~65–70% |

Slow insects and spiders switch to a wave: legs step one after another from back to front on each side. Use that for creeping or idle shuffles.

Rough cycle lengths at 30 fps (bigger creatures are slower): dog walk 24–32, trot 14–18, gallop 10–14; horse walk 30–36; game-sized insect or spider 10–20.

## Workflow

1. Plan the gait and write each leg's phase down before keying.
2. Animate one leg's full cycle (plant, push back, lift, swing forward, reach), on the leg's own controls.
3. Copy it to the other legs and shift each copy by its phase × cycle length in the Dope Sheet. Add a Cycles F-curve modifier so the shifted keys wrap around the loop.
4. Break the symmetry a little (1–2 frames, a slightly different lift per leg). Perfectly even phases look mechanical.
5. Animate the body on top (below), then run the audit with `feet=[...]` listing the lowest bone of every leg.

## Body and legs

- **Quadrupeds: two bouncing balls.** Hips ride the hind legs and the chest rides the front legs: each end dips just after one of its feet plants and rises at mid-stance. The two ends are offset by the hind-to-front phase (0.25 in a walk), so the spine rocks rather than bobbing as one block.
- **Head and tail.** In a realistic walk the head counters the chest bob to stay level. In a trot and gallop the head and neck pump with the stride. The tail lags the hips by 2–4 frames.
- **Front legs pull, hind legs push.** Front feet reach forward and plant under the head; hind feet plant under the hips and extend back.
- **Fold the swing leg.** Wrist, hock or knee must flex while the foot travels forward. A straight leg swinging past vertical dips through the floor (the audit reports FOOT BELOW FLOOR).
- **Many legs: steady body.** With 3–4 feet always down, the body moves at nearly constant speed and height. Keep the bob small, at each tripod or tetrapod switch.
- **Spiders.** Legs fan out from the body: tips move on arcs outward and back, not straight back. The front pair reaches ahead, often higher and slower, as if feeling the way.

## Sources

- Gait order and two-bouncing-ball body: [Animating Four-Legged Beasts](https://www.gamedeveloper.com/art/animating-four-legged-beasts) (after Muybridge, *Animals in Motion*).
- Horse walk, 2–3 feet down: Muybridge, [*The Attitudes of Animals in Motion*](https://www.gutenberg.org/ebooks/37743).
- Tripod gait: [Pololu, sequencing the hexapod gait](https://www.pololu.com/docs/0J42/4).
- Spider tetrapod gait and ~68% stance: [Grammostola rosea kinematics](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6935789/); alternating sets of four: [Hololena gait study](https://www.americanarachnology.org/journal-joa/joa-all-articles/article/download/arac-031-03-0428.pdf/?no_cache=1).
