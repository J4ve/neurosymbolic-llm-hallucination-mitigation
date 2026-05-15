"""Z3 wrapper: takes SMT-LIB text, returns verdict + value.

Verdicts:
  - SOLVED, value=<number>   -> unique model, problem is well-defined
  - REJECT_CONTRA            -> UNSAT, constraints contradict
  - REJECT_MISSING           -> SAT but multiple models, problem under-determined
  - ERROR                    -> parse error / timeout / malformed input
"""

from __future__ import annotations

import signal
from dataclasses import dataclass
from typing import Optional

import re

from z3 import Solver, parse_smt2_string, sat, unsat, unknown, Int, Real, Const, IntSort, RealSort


_DECLARE_RE = re.compile(r"\(declare-(?:const|fun)\s+([^\s)]+)")
_SYMBOL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
_SMT_KEYWORDS = {
    "declare-const", "declare-fun", "assert", "check-sat", "get-value",
    "get-model", "exit", "set-logic", "set-option", "Int", "Real", "Bool",
    "and", "or", "not", "true", "false", "=>", "=", "<", "<=", ">", ">=",
    "+", "-", "*", "/", "div", "mod", "ite", "let", "to_real", "to_int",
    "is_int", "abs", "distinct", "as", "pop", "push", "select", "store",
}


def repair_smtlib(text: str) -> str:
    """Add (declare-const X Int) for any symbol that is used but not declared.

    Handles a frequent failure mode of prompted translators: writing
    (assert (= total (+ a b))) without first declaring `total`. Without this,
    Z3 raises a parse error and the pipeline silently abstains.
    """
    declared = set(_DECLARE_RE.findall(text))
    used = set()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("(declare") or s.startswith("(set-") or s.startswith(";"):
            continue
        for m in _SYMBOL_RE.findall(s):
            if m in _SMT_KEYWORDS or m in declared:
                continue
            if m.isdigit():
                continue
            used.add(m)

    missing = [s for s in used if s not in declared]
    if not missing:
        return text

    decls = "\n".join(f"(declare-const {s} Int)" for s in missing)
    return decls + "\n" + text


@dataclass
class Z3Result:
    verdict: str  # SOLVED | REJECT_CONTRA | REJECT_MISSING | ERROR
    value: Optional[float] = None
    target_var: Optional[str] = None
    error: Optional[str] = None


def _has_get_value(smt_text: str) -> Optional[str]:
    """Find the variable that the SMT-LIB asks Z3 to report."""
    for line in smt_text.splitlines():
        line = line.strip()
        if line.startswith("(get-value"):
            inside = line[len("(get-value"):].strip().lstrip("(").rstrip(")")
            return inside.strip().split()[0]
    return None


def _detect_target_var(smt_text: str) -> Optional[str]:
    """Fallback: pick the last declared constant."""
    last = None
    for line in smt_text.splitlines():
        line = line.strip()
        if line.startswith("(declare-const") or line.startswith("(declare-fun"):
            parts = line.split()
            if len(parts) >= 2:
                last = parts[1]
    return last


def _check_unique_model(solver: Solver, var_const, first_value) -> bool:
    """Push a 'must differ' constraint and re-check.

    Caller passes the variable's Z3 constant (extracted before push) plus its
    value from the first model. If the re-check is UNSAT, the first model is
    the unique solution. If SAT, at least two distinct solutions exist
    -> problem is under-determined.
    """
    solver.push()
    solver.add(var_const != first_value)
    res = solver.check()
    solver.pop()
    return res == unsat


def run_smtlib(smt_text: str, timeout_s: int = 5) -> Z3Result:
    """Parse SMT-LIB, run Z3, classify result."""
    if not smt_text or not smt_text.strip():
        return Z3Result(verdict="ERROR", error="empty input")

    # Strip optional get-value / check-sat trailing commands; we control flow ourselves.
    body_lines = []
    for line in smt_text.splitlines():
        s = line.strip()
        if s.startswith("(check-sat") or s.startswith("(get-value") or s.startswith("(get-model") or s.startswith("(exit"):
            continue
        body_lines.append(line)
    body = "\n".join(body_lines)

    target_name = _has_get_value(smt_text) or _detect_target_var(smt_text)

    # Always run repair first: parse_smt2_string silently drops asserts that
    # reference undeclared symbols, so we cannot rely on it to throw.
    body = repair_smtlib(body)
    try:
        asserts = parse_smt2_string(body)
    except Exception as e:
        return Z3Result(verdict="ERROR", error=f"parse error: {e}",
                        target_var=target_name)
    if len(asserts) == 0:
        return Z3Result(verdict="ERROR", error="no assertions parsed (likely all references undefined)",
                        target_var=target_name)

    solver = Solver()
    solver.set("timeout", timeout_s * 1000)
    solver.add(asserts)

    res = solver.check()
    if res == unsat:
        return Z3Result(verdict="REJECT_CONTRA", target_var=target_name)
    if res == unknown:
        return Z3Result(verdict="ERROR", error="solver timeout/unknown", target_var=target_name)

    # SAT path: extract target value, then check uniqueness
    model = solver.model()
    if target_name is None:
        return Z3Result(verdict="ERROR", error="no target variable found", target_var=None)

    matching = [d for d in model.decls() if d.name() == target_name]
    if not matching:
        return Z3Result(verdict="ERROR", error=f"target {target_name} not in model", target_var=target_name)

    target_decl = matching[0]
    val_expr = model[target_decl]
    try:
        val_str = str(val_expr)
        # Try parse as int or fraction
        if "/" in val_str:
            num, den = val_str.split("/")
            value = float(num) / float(den)
        else:
            value = float(val_str)
    except Exception:
        value = None

    # Build the Z3 constant by name + sort, then check uniqueness
    var_const = Const(target_name, target_decl.range())
    unique = _check_unique_model(solver, var_const, val_expr)
    if not unique:
        return Z3Result(verdict="REJECT_MISSING", target_var=target_name, value=value)

    return Z3Result(verdict="SOLVED", value=value, target_var=target_name)


if __name__ == "__main__":
    # Quick sanity tests
    solvable = """
        (declare-const j Int)
        (declare-const m Int)
        (assert (= j 3))
        (assert (= m (+ j 5)))
    """
    contra = """
        (declare-const x Int)
        (assert (= x 5))
        (assert (= x 7))
    """
    missing = """
        (declare-const x Int)
        (declare-const y Int)
        (assert (> x 0))
        (assert (= y (+ x 1)))
    """

    for name, smt in [("solvable->m", solvable), ("contra", contra), ("missing", missing)]:
        # For solvable, point Z3 at 'm'
        if name == "solvable->m":
            smt = smt + "\n(get-value (m))\n"
        r = run_smtlib(smt)
        print(f"{name:20s} -> {r}")
