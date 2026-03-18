from sentinel.infrastructure.tools.packages.transaction_parser import PackageTransactionParser


def test_pacman_parser_builds_expected_preview() -> None:
    parser = PackageTransactionParser()
    assert parser.preview("install", ["ripgrep", "fd"]) == "pacman -S ripgrep fd"
    assert parser.preview("remove", ["vim"]) == "pacman -R vim"
    assert parser.preview("upgrade", []) == "pacman -Syu"
