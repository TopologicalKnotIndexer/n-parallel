"""Remove explicit Reidemeister-I crossings while preserving label order."""

from __future__ import annotations


def _renumber_in_numeric_order(pd_code: list[list[int]]) -> list[list[int]]:
    labels = sorted({label for crossing in pd_code for label in crossing})
    mapping = {label: index + 1 for index, label in enumerate(labels)}
    return [[mapping[label] for label in crossing] for crossing in pd_code]


def de_r1(pd_code: list[list[int]]) -> list[list[int]]:
    result = [list(crossing) for crossing in pd_code]
    while True:
        index = next(
            (i for i, crossing in enumerate(result) if len(set(crossing)) <= 3),
            None,
        )
        if index is None:
            return _renumber_in_numeric_order(result)

        crossing = result.pop(index)
        singles = [label for label in crossing if crossing.count(label) == 1]
        if len(singles) == 2:
            keep, replace = min(singles), max(singles)
            result = [
                [keep if label == replace else label for label in other]
                for other in result
            ]
        elif len(singles) != 0:
            raise ValueError(f"unsupported degenerate R1 crossing: {crossing!r}")


if __name__ == "__main__":
    import ast

    print(de_r1(ast.literal_eval(input("pd_code>>>"))))
