# superzipy
Iterate multiple iterable by row, with defaults and previous values.


# Usage

```python
from superzip import ziplus
for (a, b, c) in ziplus(range(10), reversed(range(1, 10)), "abcdef",
                        defaults=(None, None, ziplus.Previous)):
    print(a, b, c)

```

Renders.....
```
0 9 a
1 8 b
2 7 c
3 6 d
4 5 e
5 4 f
6 3 f
7 2 f
8 1 f
9 None f

```

```python
help(ziplus)
```

Renders.....
```
Help on function ziplus in module superzip:

ziplus(*iterables, defaults=None, debug=False)
    Iterate multiple iterables by row, with defaults and previous values.
    
    Same as zip but with the addition it can iterate the rows for the longest
    lived iterable item using either defaults or the previous row.
    
    Arguments:
        *iterables (list[Iterables]:) the column iterables.
        defaults (list[any]:) the default or control value (see notes).
        debug (bool:) print out state details.
    
    Notes:
        defaults can be any value including None, or one of the recognized
        control Values, namely StopIteration, Previous or an exception.  The
        "Previous" control value is attached as an attribute to both the module
        and ziplus function (fe. ziplus.Previous).  StopIteration stops
        iteration when it's column is exhausted and is the python builtin
        StopItertion exception which can be used directly.  In addition a
        default can be a non-StopIteration exception instance which will cause
        that exception to be raised.
    
    Examples:
        >>> for (a,b,c) in ziplus(range(10), reversed(range(10)), 'abcdef',
                                  defaults=(ziplus.Previous, StopIteration,
                                  ziplus.Previous)):
        ...     print(a, b, c)

```
