"""Print a fixed tide table."""

TIDES = [("high", "04:12"), ("low", "10:31"), ("high", "16:45"), ("low", "22:58")]


def main() -> None:
    for kind, at in TIDES:
        print(f"{kind:>4} {at}")


if __name__ == "__main__":
    main()
