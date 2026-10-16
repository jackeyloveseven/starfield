"""TEMP test harness (not a deliverable): force every body in a copy to one kind
so each appearance can be inspected on its own. Rewrites only the roll line."""
import sys
src = open(sys.argv[1], encoding='utf-8').read()
A = """  const roll=r();
  let kind=roll<.26?0:roll<.44?1:roll<.60?2:roll<.72?3
          :roll<.78?5:roll<.87?6:roll<.90?7:roll<.95?8:4;"""
assert src.count(A) == 1, src.count(A)
for k in range(9):
    out = 'work-kind%d.html' % k
    open(out, 'w', encoding='utf-8', newline='').write(
        src.replace(A, "  const roll=r();\n  let kind=%d;" % k, 1))
    print('wrote', out)
