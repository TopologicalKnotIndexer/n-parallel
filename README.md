# n-parallel

`n-parallel` computes an `n`-parallel of a knot or link planar diagram (PD)
code. Every component is replaced by `n` parallel components and every
remaining crossing is replaced by an `n × n` crossing block.

The implementation is pure Python and has no third-party runtime dependencies.

## PD Convention

Each crossing is written as four labels beginning with the incoming under-arc
and continuing clockwise. Along every oriented component, labels must form one
consecutive integer interval. The full PD code must use exactly the labels
`1..2c`, and every label must occur twice.

There are two local crossing forms. If `b+` and `a+` denote successors along
their components and `a-` denotes the predecessor of `a`, they are:

```text
[b, a, b+, a-]
[b, a, b+, a+]
```

Both forms are expanded independently into the corresponding cable crossing
matrix. Labels are then renumbered while preserving their total order.

## Python API

```python
from n_parallel import n_parallel

trefoil = [[1, 5, 2, 4], [3, 1, 4, 6], [5, 3, 6, 2]]
parallel = n_parallel(trefoil, 2)
print(parallel)
```

## Command Line

Run the package module from the repository root:

```sh
python -m n_parallel 2 "[[1,5,2,4],[3,1,4,6],[5,3,6,2]]"
```

The result is written as compact JSON.

## Cabling, Doubling, and Framing

A general `(p,q)` cable is a satellite construction on the boundary of a
tubular neighborhood, with its slope measured relative to a chosen meridian
and preferred longitude. That operation is not implemented here: there is no
`q` parameter and no strand-closing braid that would construct a general cable
knot.

The local `n × n` replacement in this repository instead constructs parallel
copies of the input diagram. A direct blackboard parallel depends on diagram
framing because an R1 move changes writhe. The historical implementation first
removes explicit R1 kinks, and this behavior is retained so diagrams differing
only by those reducible kinks produce the same output.

This R1 normalization should not be confused with a complete preferred-longitude
framing calculation. Callers that require a mathematically specified `(p,q)`
cable must supply the corresponding framing/twist construction separately.
A crossingless component cannot be represented faithfully by ordinary PD
crossings; therefore `PD[]` returns `[]` and does not encode the number of
parallel components.

## Tests

```sh
python -m unittest discover -s tests -v
```

The suite checks one-cable identity, both crossing orientations, crossing-count
growth, label multiplicities, R1 normalization, and invalid input handling.

## Citation

If you use this repository in academic work, please cite it as:

```bibtex
@software{topologicalknotindexer_n_parallel,
  author = {{TopologicalKnotIndexer contributors}},
  title = {{n-parallel}},
  year = {2026},
  url = {https://github.com/TopologicalKnotIndexer/n-parallel}
}
```
