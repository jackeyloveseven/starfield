"""V119: the departure dolly on simulated time, so it can be verified.

The dolly was driven by wall-clock timestamps inside frame(). rAF does not run
in a headless virtual-time dump, so nothing that animates there can be checked -
and the arrival is exactly the part worth checking. It now advances by dt:

    stepDeparture(dt)   called from frame(realDt) and from seek(step)

which makes the landing testable: click a chip, seek three seconds, and travel
must equal that region's anchor.

Run:  python -I v119_depart2.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()


def rep(a, b):
    global src
    n = src.count(a)
    if n != 1:
        sys.exit("count=%d (want 1): %r" % (n, a[:120]))
    src = src.replace(a, b, 1)


# the dolly, as a stepper
rep("""function __departDolly(i){
 const from=travel, to=i*SEGMENT+SEGMENT*.5;""",
    """function stepDeparture(dt){
 if(!__depart)return;
 __depart.k=Math.min(1,__depart.k+dt/__depart.dur);
 const k=__depart.k;
 const e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;   // easeInOutCubic
 travel=__depart.from+(__depart.to-__depart.from)*e;
 if(k>=1){const i=__depart.i;__depart=null;chooseDeparture(i);}
}
function __departDolly(i){
 const from=travel, to=i*SEGMENT+SEGMENT*.5;""")

rep(""" __depart={from:from,to:to,i:i,t0:performance.now(),dur:Math.min(2200,700+Math.abs(to-from)/14)};""",
    """ __depart={from:from,to:to,i:i,k:0,dur:Math.min(2200,700+Math.abs(to-from)/14)};""")

# frame(): drive it by realDt
rep(""" if(__depart){
  const k=Math.min(1,(now-__depart.t0)/__depart.dur);
  const e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;   // easeInOutCubic
  travel=__depart.from+(__depart.to-__depart.from)*e;
  if(k>=1){const i=__depart.i;__depart=null;chooseDeparture(i);}
 }""",
    """ stepDeparture(realDt);""")

# seek(): same stepper, same simulated clock
rep("""   if(tessT>0){tessT+=step;if(tessT>TESS_DUR)tessT=0;}""",
    """   if(tessT>0){tessT+=step;if(tessT>TESS_DUR)tessT=0;}
   stepDeparture(step);""")

# a public stepper, next to seek(): the only way a headless probe can advance
# an intro animation, since rAF does not run in a virtual-time dump
rep(""" seek:(seconds""", """ stepDeparture:(dt)=>stepDeparture(dt),
 seek:(seconds""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V119 written:", len(src), "chars")
