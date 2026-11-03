"""Check forbidden imports with the Python standard library; fail closed on syntax errors."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def imports(tree: ast.AST, module: str, is_package: bool) -> list[tuple[int, str]]:
    results: list[tuple[int, str]] = []
    package_parts = module.split(".") if is_package else module.split(".")[:-1]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            results.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                up = node.level - 1
                base = package_parts[: len(package_parts) - up] if up <= len(package_parts) else []
                if not base:
                    results.append((node.lineno, "<invalid-relative-import>"))
                    continue
                prefix = ".".join([*base, *([node.module] if node.module else [])])
            else:
                prefix = node.module or ""
            results.append((node.lineno, prefix))
            if node.module is None:
                results.extend((node.lineno, f"{prefix}.{alias.name}") for alias in node.names if alias.name != "*")
    return results


def check(root: Path, config: dict) -> list[dict]:
    violations: list[dict] = []
    forbidden = tuple(config["forbidden_import_prefixes"])
    exemptions = set(config.get("exemptions", []))
    for scan_root in config["scan_roots"]:
        directory = root / scan_root
        if not directory.is_dir():
            violations.append({"file": scan_root, "line": 0, "reason": "scan root missing"})
            continue
        for path in sorted(directory.rglob("*.py")):
            relative = path.relative_to(root).as_posix()
            module = ".".join(path.relative_to(root).with_suffix("").parts)
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
            except (SyntaxError, UnicodeError) as exc:
                violations.append({"file": relative, "line": getattr(exc, "lineno", 0) or 0, "reason": "invalid Python source"})
                continue
            for lineno, imported in imports(tree, module, path.name == "__init__.py"):
                if imported.startswith("<invalid-") or any(imported == prefix or imported.startswith(prefix + ".") for prefix in forbidden):
                    if f"{relative}:{lineno}:{imported}" not in exemptions:
                        violations.append({"file": relative, "line": lineno, "reason": f"forbidden import: {imported}"})
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--policy", default="architecture/policies/dependency-rules.json")
    parser.add_argument("--report", default="architecture-evidence.json")
    args = parser.parse_args()
    root = args.root.resolve()
    config = json.loads((root / args.policy).read_text(encoding="utf-8"))
    findings = check(root, config)
    result = {"schema_version": "1.0", "rule_id": config["rule_id"], "status": "FAIL" if findings else "PASS", "violations": findings}
    report = Path(args.report)
    if not report.is_absolute():
        report = root / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
