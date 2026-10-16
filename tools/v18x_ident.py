"""Identification probe (read-only w.r.t. the real artwork).

Question: what draws the horizontal band of white spiky shapes across the
middle of v16-close.png (y~370-450, x~320-1150)?

Method: take the live file's copy (work-ident.html), emit two probe copies -
one with drawFleet() early-returned, one with drawParticles() early-returned -
then screenshot the exact same (seed, at, seek) frame and compare the band.
"""
import os, shutil, subprocess, sys

WORK = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(WORK, 'work-ident.html')

# Anchor: the first statement inside drawFleet's for-loop is unique.
FLEET_ANCHOR = "function drawFleet(){\n for(const b of fleet){\n  const pos=craftWorld(b),p=region(pos[0],pos[2]);"
FLEET_PATCH = "function drawFleet(){\n if(true)return;\n for(const b of fleet){\n  const pos=craftWorld(b),p=region(pos[0],pos[2]);"

PART_ANCHOR = "function drawParticles(){\n for(const p of particles){"
PART_PATCH = "function drawParticles(){\n if(true)return;\n for(const p of particles){"


def emit(out, anchor, patch):
    src = open(SRC, encoding='utf-8').read()
    assert src.count(anchor) == 1, (anchor[:40], src.count(anchor))
    open(out, 'w', encoding='utf-8', newline='').write(src.replace(anchor, patch, 1))
    print('wrote', out)


emit(os.path.join(WORK, 'work-ident-nofleet.html'), FLEET_ANCHOR, FLEET_PATCH)
emit(os.path.join(WORK, 'work-ident-noparts.html'), PART_ANCHOR, PART_PATCH)
print('ok')
