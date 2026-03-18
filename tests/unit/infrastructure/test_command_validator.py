from sentinel.infrastructure.tools.terminal.validator import TerminalCommandValidator


def test_command_validator_blocks_shell_and_denied_binaries() -> None:
    validator = TerminalCommandValidator({"sudo", "rm"})
    violations = validator.validate("sudo", ["-n", "echo", "hi"])
    assert any("binary denied" in violation for violation in violations)

    shell_violations = validator.validate("bash", ["-lc", "echo hi"])
    assert any("raw shell interpreters" in violation for violation in shell_violations)


def test_command_validator_allows_structured_read_command() -> None:
    validator = TerminalCommandValidator({"sudo", "rm"})
    assert validator.validate("ls", ["-la", "/tmp"]) == []
