#!/usr/bin/env python3
"""Safely scan and clean reproducible macOS caches, rotated logs, and Docker data."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

GIB = 1024**3
MIB = 1024**2
DEFAULT_CATEGORIES = ("dev-caches", "user-logs", "docker")
CONFIRM_TOKEN = "DELETE-CACHE-ONLY"


@dataclass(frozen=True)
class Candidate:
    category: str
    path: str
    size_bytes: int
    reason: str


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    succeeded: bool
    output: str


def home_path() -> Path:
    override = os.environ.get("CACHE_CLEANER_HOME")
    return Path(override).expanduser().resolve() if override else Path.home().resolve()


def development_cache_roots(home: Path) -> tuple[Path, ...]:
    return (
        home / ".cache",
        home / ".npm",
        home / "Library/Caches/go-build",
        home / "Library/Caches/JetBrains",
        home / "Library/Caches/ms-playwright",
        home / "Library/pnpm/store",
    )


def user_log_roots(home: Path) -> tuple[Path, ...]:
    return (
        home / "Library/Logs/JetBrains",
        home / "Library/Logs/com.openai.codex",
        home / "Library/Logs/workbuddy-ai",
        home / ".claude-mem/logs",
    )


def protected_roots(home: Path) -> tuple[Path, ...]:
    return (
        home / "Documents",
        home / "Desktop",
        home / "Pictures",
        home / "Movies",
        home / "Music",
        home / "Library/Containers/com.tencent.xinWeChat",
        home / "Library/Application Support/Postman",
    )


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def ensure_allowed(path: Path, allowed_roots: Iterable[Path], home: Path) -> None:
    resolved = path.resolve(strict=False)
    if any(is_relative_to(resolved, root.resolve(strict=False)) for root in protected_roots(home)):
        raise ValueError(f"受保护路径不能清理：{resolved}")
    if not any(is_relative_to(resolved, root.resolve(strict=False)) for root in allowed_roots):
        raise ValueError(f"路径不在清理白名单：{resolved}")


def path_size(path: Path) -> int:
    if not path.exists() and not path.is_symlink():
        return 0
    if path.is_file() or path.is_symlink():
        try:
            return path.lstat().st_size
        except OSError:
            return 0
    total = 0
    for root, _, files in os.walk(path, followlinks=False):
        for name in files:
            try:
                total += (Path(root) / name).lstat().st_size
            except OSError:
                continue
    return total


def format_size(size: int) -> str:
    if size >= GIB:
        return f"{size / GIB:.2f} GiB"
    if size >= MIB:
        return f"{size / MIB:.1f} MiB"
    return f"{size / 1024:.1f} KiB"


def iter_rotated_logs(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return ()
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if name.endswith((".gz", ".zip")) or ".log." in name or name.startswith("threadumps-"):
            candidates.append(path)
        elif "threaddumps-" in str(path.parent).lower():
            candidates.append(path)
    return tuple(candidates)


def scan_filesystem(categories: set[str], home: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    if "dev-caches" in categories:
        for root in development_cache_roots(home):
            size = path_size(root)
            if size:
                candidates.append(Candidate("dev-caches", str(root), size, "可重建的开发工具缓存"))
    if "user-logs" in categories:
        for root in user_log_roots(home):
            for path in iter_rotated_logs(root):
                size = path_size(path)
                if size:
                    candidates.append(Candidate("user-logs", str(path), size, "明确的历史或轮转日志"))
    return candidates


def run(command: tuple[str, ...]) -> CommandResult:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return CommandResult(command, False, f"命令不存在：{command[0]}")
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    return CommandResult(command, completed.returncode == 0, output)


def docker_scan() -> dict[str, object]:
    system_df = run(("docker", "system", "df"))
    buildx_du = run(("docker", "buildx", "du"))
    return {"system_df": asdict(system_df), "buildx_du": asdict(buildx_du)}


def clear_directory_contents(root: Path, home: Path) -> int:
    ensure_allowed(root, development_cache_roots(home), home)
    removed = path_size(root)
    if not root.is_dir():
        return 0
    for child in root.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)
    return removed


def remove_log(path: Path, home: Path) -> int:
    ensure_allowed(path, user_log_roots(home), home)
    if path not in iter_rotated_logs(next(root for root in user_log_roots(home) if is_relative_to(path, root))):
        raise ValueError(f"不是明确的历史或轮转日志：{path}")
    removed = path_size(path)
    path.unlink(missing_ok=True)
    return removed


def docker_clean() -> list[CommandResult]:
    commands = (
        ("docker", "buildx", "prune", "--all", "--force"),
        ("docker", "image", "prune", "--all", "--force"),
        ("docker", "container", "prune", "--force"),
    )
    return [run(command) for command in commands]


def disk_usage() -> CommandResult:
    return run(("df", "-h", "/System/Volumes/Data"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="安全扫描或清理 macOS 缓存、轮转日志和 Docker 可回收数据")
    parser.add_argument("--mode", choices=("scan", "clean"), default="scan")
    parser.add_argument("--categories", nargs="+", choices=("dev-caches", "user-logs", "docker"), default=list(DEFAULT_CATEGORIES))
    parser.add_argument("--confirm", help=f"执行清理时必须精确输入 {CONFIRM_TOKEN}")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home = home_path()
    categories = set(args.categories)
    filesystem_candidates = scan_filesystem(categories, home)
    report: dict[str, object] = {
        "mode": args.mode,
        "categories": sorted(categories),
        "filesystem_candidates": [asdict(item) for item in filesystem_candidates],
        "filesystem_candidate_bytes": sum(item.size_bytes for item in filesystem_candidates),
        "docker": docker_scan() if "docker" in categories else None,
        "disk_before": asdict(disk_usage()),
        "enterprise_logs": "未扫描或清理；DLP 等企业安全组件日志需要单独明确授权",
    }

    if args.mode == "clean":
        if args.confirm != CONFIRM_TOKEN:
            print(f"拒绝执行：请在用户明确确认后添加 --confirm {CONFIRM_TOKEN}", file=sys.stderr)
            return 2
        removed_bytes = 0
        errors: list[str] = []
        if "dev-caches" in categories:
            for root in development_cache_roots(home):
                try:
                    removed_bytes += clear_directory_contents(root, home)
                except (OSError, ValueError) as error:
                    errors.append(str(error))
        if "user-logs" in categories:
            for candidate in filesystem_candidates:
                if candidate.category != "user-logs":
                    continue
                try:
                    removed_bytes += remove_log(Path(candidate.path), home)
                except (OSError, ValueError, StopIteration) as error:
                    errors.append(str(error))
        docker_results = docker_clean() if "docker" in categories else []
        report = {
            **report,
            "removed_filesystem_bytes": removed_bytes,
            "docker_clean": [asdict(item) for item in docker_results],
            "errors": errors,
            "filesystem_after": [asdict(item) for item in scan_filesystem(categories, home)],
            "docker_after": docker_scan() if "docker" in categories else None,
            "disk_after": asdict(disk_usage()),
        }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"模式：{args.mode}")
        print(f"文件系统候选：{len(filesystem_candidates)} 项，约 {format_size(report['filesystem_candidate_bytes'])}")
        for item in sorted(filesystem_candidates, key=lambda value: value.size_bytes, reverse=True):
            print(f"- [{item.category}] {format_size(item.size_bytes):>10}  {item.path}")
        if report.get("docker"):
            docker_report = report["docker"]
            print("\nDocker 空间报告：")
            print(docker_report["system_df"]["output"] or "无法读取 Docker 空间")
            print("\nBuildKit 空间报告：")
            print(docker_report["buildx_du"]["output"] or "无法读取 BuildKit 空间")
        print(f"\n企业组件：{report['enterprise_logs']}")
        if args.mode == "clean":
            print(f"\n文件系统已处理约：{format_size(report['removed_filesystem_bytes'])}")
            if report["errors"]:
                print("未完成项：")
                for error in report["errors"]:
                    print(f"- {error}")
            print("\n清理后磁盘：")
            print(report["disk_after"]["output"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
