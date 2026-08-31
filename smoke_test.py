"""Run quick non-network checks for the Jarvis Briefing server."""

from __future__ import annotations

import argparse

from server import (
    MAX_STOCK_SYMBOLS,
    parse_stock_symbols,
    stock_row_from_chart,
    valid_port,
)


def assert_argparse_error(func, value: str, expected_message: str) -> None:
    try:
        func(value)
    except argparse.ArgumentTypeError as exc:
        if expected_message not in str(exc):
            raise AssertionError(f"Unexpected parser error: {exc}") from exc
    else:
        raise AssertionError(f"Expected {value!r} to fail validation.")


def assert_value_error(func, value: str, expected_message: str) -> None:
    try:
        func(value)
    except ValueError as exc:
        if expected_message not in str(exc):
            raise AssertionError(f"Unexpected validation error: {exc}") from exc
    else:
        raise AssertionError(f"Expected {value!r} to fail validation.")


def assert_formats_stock_row() -> None:
    result = {
        "meta": {"symbol": "msft", "shortName": "Microsoft"},
        "indicators": {"quote": [{"close": [99.0, None, 101.0]}]},
    }
    assert stock_row_from_chart(result, "MSFT") == {
        "symbol": "MSFT",
        "name": "Microsoft",
        "price": "101.00",
        "change": "+2.02%",
        "updated": "",
    }
    assert stock_row_from_chart({}, "MISSING") == {
        "symbol": "MISSING",
        "name": "MISSING",
        "price": "N/A",
        "change": "N/A",
        "updated": "",
    }


def main() -> None:
    assert valid_port("8765") == 8765
    assert_argparse_error(valid_port, "0", "between 1 and 65535")
    assert_argparse_error(valid_port, "70000", "between 1 and 65535")
    assert_argparse_error(valid_port, "local", "must be an integer")

    assert parse_stock_symbols("aapl, BRK-B, ^gspc") == [
        "AAPL",
        "BRK-B",
        "^GSPC",
    ]
    assert parse_stock_symbols("aapl, AAPL, msft") == ["AAPL", "MSFT"]
    assert_value_error(parse_stock_symbols, "", "No symbols provided")
    assert_value_error(parse_stock_symbols, "AAPL,$BAD", "Invalid stock symbol")
    too_many_symbols = ",".join(f"TICK{i}" for i in range(MAX_STOCK_SYMBOLS + 1))
    assert_value_error(parse_stock_symbols, too_many_symbols, "Too many symbols")
    assert_formats_stock_row()

    print("Smoke checks passed.")


if __name__ == "__main__":
    main()
