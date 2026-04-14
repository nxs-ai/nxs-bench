from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path as PathlibPath
from typing import Any, Callable


class ClickException(Exception):
    pass


def echo(message: Any = "") -> None:
    print(message)


class Path:
    def __init__(self, *, exists: bool = False, path_type: type = str):
        self.exists = exists
        self.path_type = path_type

    def convert(self, value: str):
        converted = self.path_type(value)
        if self.exists and hasattr(converted, "exists") and not converted.exists():
            raise ClickException(f"Path does not exist: {value}")
        return converted


@dataclass
class OptionSpec:
    flags: list[str]
    name: str
    required: bool = False
    default: Any = None
    option_type: Any = str
    multiple: bool = False

    def convert(self, raw: list[str] | None):
        if self.multiple:
            raw_values = raw or []
            return tuple(self._convert_one(item) for item in raw_values)
        if raw is None or len(raw) == 0:
            return self.default
        return self._convert_one(raw[-1])

    def _convert_one(self, value: str):
        if isinstance(self.option_type, Path):
            return self.option_type.convert(value)
        if self.option_type is int:
            return int(value)
        if self.option_type is float:
            return float(value)
        return value


def option(*param_decls, **kwargs):
    explicit_name = next((decl for decl in param_decls if not str(decl).startswith("-")), None)
    flags = [decl for decl in param_decls if str(decl).startswith("-")]
    if explicit_name is None and flags:
        explicit_name = flags[0].lstrip("-").replace("-", "_")
    spec = OptionSpec(
        flags=flags,
        name=str(explicit_name),
        required=kwargs.get("required", False),
        default=kwargs.get("default"),
        option_type=kwargs.get("type", str),
        multiple=kwargs.get("multiple", False),
    )

    def decorator(func: Callable):
        specs = getattr(func, "__click_options__", [])
        specs.insert(0, spec)
        setattr(func, "__click_options__", specs)
        return func

    return decorator


class Command:
    def __init__(self, callback: Callable, name: str | None = None):
        self.callback = callback
        self.name = name or callback.__name__.replace("_", "-")
        self.options: list[OptionSpec] = list(getattr(callback, "__click_options__", []))

    def invoke(self, argv: list[str]) -> Any:
        kwargs = _parse_options(self.options, argv)
        return self.callback(**kwargs)


class Group(Command):
    def __init__(self, callback: Callable, name: str | None = None):
        super().__init__(callback, name=name or callback.__name__.replace("_", "-"))
        self.commands: dict[str, Command] = {}

    def command(self, name: str | None = None):
        def decorator(func: Callable):
            command = Command(func, name=name)
            self.commands[command.name] = command
            return command

        return decorator

    def invoke(self, argv: list[str]) -> Any:
        if not argv:
            return self.callback()
        command_name = argv[0]
        command = self.commands.get(command_name)
        if command is None:
            raise ClickException(f"Unknown command: {command_name}")
        return command.invoke(argv[1:])


def group():
    def decorator(func: Callable):
        return Group(func)

    return decorator


def command(name: str | None = None):
    def decorator(func: Callable):
        return Command(func, name=name)

    return decorator


@dataclass
class Result:
    output: str
    exit_code: int
    exception: Exception | None = None


class CliRunner:
    def invoke(self, cli: Command, args: list[str] | tuple[str, ...] | None = None) -> Result:
        argv = list(args or [])
        stdout = io.StringIO()
        stderr = io.StringIO()
        exception: Exception | None = None
        exit_code = 0
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                cli.invoke(argv)
            except ClickException as exc:
                exception = exc
                exit_code = 1
                echo(str(exc))
            except SystemExit as exc:
                exception = exc
                exit_code = int(exc.code) if isinstance(exc.code, int) else 1
            except Exception as exc:  # pragma: no cover - surfaced in tests when unexpected
                exception = exc
                exit_code = 1
                echo(str(exc))
        return Result(output=stdout.getvalue() + stderr.getvalue(), exit_code=exit_code, exception=exception)


def _parse_options(specs: list[OptionSpec], argv: list[str]) -> dict[str, Any]:
    consumed: dict[str, list[str]] = {}
    index = 0
    flag_lookup = {flag: spec for spec in specs for flag in spec.flags}

    while index < len(argv):
        token = argv[index]
        if token.startswith("-"):
            spec = flag_lookup.get(token)
            if spec is None:
                raise ClickException(f"Unknown option: {token}")
            if index + 1 >= len(argv):
                raise ClickException(f"Option requires a value: {token}")
            consumed.setdefault(spec.name, []).append(argv[index + 1])
            index += 2
            continue
        raise ClickException(f"Unexpected argument: {token}")

    kwargs: dict[str, Any] = {}
    for spec in specs:
        value = consumed.get(spec.name)
        if value is None and spec.required and spec.default is None:
            raise ClickException(f"Missing option: --{spec.name.replace('_', '-')}")
        kwargs[spec.name] = spec.convert(value)
    return kwargs


__all__ = [
    "CliRunner",
    "ClickException",
    "Command",
    "Group",
    "Path",
    "Result",
    "command",
    "echo",
    "group",
    "option",
]
