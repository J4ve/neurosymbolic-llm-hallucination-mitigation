"""Debug: try repair on a known-broken SMT-LIB and see what happens."""

from z3 import parse_smt2_string
from z3_runner import repair_smtlib, run_smtlib


broken = """(declare-const cats Int)
(declare-const dogs Int)
(declare-const rabbits Int)
(declare-const fish Int)
(declare-const gerbils Int)
(assert (= cats 3))
(assert (= dogs (* 3 cats)))
(assert (= rabbits (- dogs 2)))
(assert (= fish (* 3 rabbits)))
(assert (= gerbils (/ fish 3)))
(assert (= total (+ cats dogs rabbits fish gerbils)))
(check-sat)
(get-value (total))
"""

print("=== BROKEN ===")
print(broken)
print("\n=== REPAIRED ===")
print(repair_smtlib(broken))

print("\n=== Z3 RESULT (via run_smtlib) ===")
r = run_smtlib(broken)
print(r)


broken2 = """(declare-const dallas Int)
(declare-const darla Int)
(declare-const given-to-darla Int)
(assert (= dallas 21))
(assert (= (+ dallas given-to-darla) 52))
(check-sat)
(get-value (given-to-darla))
"""
print("\n=== HYPHEN CASE ===")
r = run_smtlib(broken2)
print(r)
