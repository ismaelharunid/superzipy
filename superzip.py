from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generator_stop

try:
    from collections.abc import Iterable, Sequence
except ImportError:
    from collections import Iterable, Sequence


Previous = type("PreviousType", (object,), {})()


def ziplus(*iterables, defaults=None, debug=False):
    """
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
        ...
        0 9 a
        1 8 b
        2 7 c
        3 6 d
        4 5 e
        5 4 f
        6 3 f
        7 2 f
        8 1 f
        9 0 f
        >>> for (a,b,c) in ziplus(range(10), reversed(range(10)), 'abcdef',
                                  defaults=(ziplus.Previous, StopIteration,
                                            None)):
        ...     print(a, b, c)
        ...
        0 9 a
        1 8 b
        2 7 c
        3 6 d
        4 5 e
        5 4 f
        6 3 None
        7 2 None
        8 1 None
        9 0 None
        >>> for (a,b,c) in ziplus(range(10), reversed(range(5)), 'abcdef',
                                  defaults=(ziplus.Previous, ziplus.Previous,
                                            StopIteration)):
        ...   print(a, b, c)
        ...
        0 9 a
        1 8 b
        2 7 c
        3 6 d
        4 5 e
        5 4 f
        >>> for (a,b,c) in ziplus(range(10), reversed(range(5)), 'abcdef',
                                  defaults=(ziplus.Previous, ziplus.Previous,
                                            IndexError("Oh no!"))):
        ...   print(a, b, c)
        ...
        0 4 a
        1 3 b
        2 2 c
        3 1 d
        4 0 e
        5 0 f
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File ".../superzip.py", line 136, in ziplus
            raise defaults[i]
        IndexError: Oh no!
    """
    n_items = len(iterables)
    if defaults is None:
        defaults = (StopIteration,) * n_items
    if not isinstance(defaults, Sequence):
        raise ValueError("defaults expects a Sequence but found {:}"
                         .format(type(defaults).__name__))
    if len(defaults) != n_items:
        raise ValueError("Bad defaults length")
    items = tuple(iter(i if isinstance(i, Iterable) else (i,))
                  for i in iterables)
    i_items = tuple(range(n_items))
    n_stopped = 0
    stopped = [False] * n_items
    i_rows = 0
    values = []
    for i in i_items:
        if stopped[i] is False:
            try:
                values.append(items[i].__next__())
                continue
            except StopIteration:
                stopped[i] = True
                n_stopped += 1
                if debug:
                    print("StopIteration at "
                          "(row {:d}, column {:d}), {:d} of {:d} now stopped"
                          .format(i_rows, i, n_stopped, n_items))
                if defaults[i] is StopIteration:
                    if debug:
                        print("Full stop at (row {:d}, column {:d})"
                              .format(i_rows, i))
                    return
        if isinstance(defaults[i], Exception):
            raise defaults[i]
        values.append(None if defaults[i] is Previous else defaults[i])
    while n_stopped < n_items:
        if debug:
            print('row {:d}, {:d} of {:d} stopped, values: {:s}'
                  .format(i_rows, n_stopped, n_items, repr(values)))
        yield values
        i_rows += 1
        previous = values
        values = []
        for i in i_items:
            if stopped[i] is False:
                try:
                    values.append(items[i].__next__())
                    continue
                except StopIteration:
                    stopped[i] = True
                    n_stopped += 1
                    if debug:
                        print("StopIteration at (row "
                              "{:d}, column {:d}), {:d} of {:d} now stopped"
                              .format(i_rows, i, n_stopped, n_items))
                    if defaults[i] is StopIteration:
                        if debug:
                            print("Full stop at (row {:d}, column {:d})"
                                  .format(i_rows, i))
                        return
            if isinstance(defaults[i], Exception):
                raise defaults[i]
            values.append(previous[i] if defaults[i] is Previous else
                          defaults[i])
    if debug:
        print('loop(end)', n_items, n_stopped)


setattr(ziplus, "Previous", Previous)
setattr(ziplus, "StopIteration", StopIteration)


def test_ziplus(debug=False):
    #             (((iterables,
    #               (defaults,
    #               ((expected))))))
    testvalues = (((range(10), reversed(range(10)), 'abcdef'),
                   None,
                   ([0, 9, "a"],
                    [1, 8, "b"],
                    [2, 7, "c"],
                    [3, 6, "d"],
                    [4, 5, "e"],
                    [5, 4, "f"])),
                  ((range(10), reversed(range(10)), 'abcdef'),
                   (ziplus.Previous,) * 3,
                   ([0, 9, "a"],
                    [1, 8, "b"],
                    [2, 7, "c"],
                    [3, 6, "d"],
                    [4, 5, "e"],
                    [5, 4, "f"],
                    [6, 3, "f"],
                    [7, 2, "f"],
                    [8, 1, "f"],
                    [9, 0, "f"])),
                  ((range(10), reversed(range(10)), 'abcdef'),
                   (ziplus.Previous, None, ziplus.StopIteration),
                   ([0, 9, "a"],
                    [1, 8, "b"],
                    [2, 7, "c"],
                    [3, 6, "d"],
                    [4, 5, "e"],
                    [5, 4, "f"])),
                  ((range(10), reversed(range(10)), 'abcdef'),
                   (ziplus.Previous, ziplus.StopIteration, None),
                   ([0, 9, "a"],
                    [1, 8, "b"],
                    [2, 7, "c"],
                    [3, 6, "d"],
                    [4, 5, "e"],
                    [5, 4, "f"],
                    [6, 3, None],
                    [7, 2, None],
                    [8, 1, None],
                    [9, 0, None])),
                  ((range(10), reversed(range(10)), 'abcdef'),
                   (ziplus.Previous, ziplus.StopIteration,
                    IndexError('Oh no!')),
                   ([0, 9, "a"],
                    [1, 8, "b"],
                    [2, 7, "c"],
                    [3, 6, "d"],
                    [4, 5, "e"],
                    [5, 4, "f"])))
    test = counts = success = failure = errors = 0
    template = "Test {:d}, row {:d} expected {:s}, actual {:s}"
    for (iterables, defaults, expected) in testvalues:
        n_items = len(iterables)
        n_expected = len(expected)
        if debug:
            print("================== Test {:d} =================="
                  .format(test))
        row = 0
        try:
            for values in ziplus(*iterables, defaults=defaults, debug=debug):
                try:
                    msg = template.format(test, row, repr(expected[row]),
                                          repr(values))
                    assert all(values[i] == expected[row][i]
                               for i in range(n_items)), "[FAIL] " + msg
                    success += 1
                    if debug:
                        print("[PASS] " + msg)
                except AssertionError as aexc:
                    if len(aexc.args) and aexc.args[0] \
                            .startswith("[Fail] Test"):
                        failure += 1
                    else:
                        errors += 1
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    if debug:
                        print("[ERR ]", repr(aexc), "line {:d}"
                              .format(exc_tb.tb_lineno))
                except Exception as exc:
                    errors += 1
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    if debug:
                        print("[ERR ]", repr(exc), "line {:d}"
                              .format(exc_tb.tb_lineno))
                row += 1
                counts += 1
            if row != n_expected:
                failure += 1
                if debug:
                    print("[FAIL] expected {:d} rows, found {:d}"
                          .format(n_expected, row))
            test += 1
        except Exception as exc:
            if defaults and exc in defaults:
                if row != n_expected:
                    failure += 1
                    if debug:
                        print("[FAIL] expected {:s}"
                              .format(exc))
                test += 1
                if debug:
                    print("[PASS] " + repr(exc))
    if debug or errors or counts != success:
        print("{} tests, {} values, {} passed, {} failed and {:d} errors"
              .format(test, counts, success, failure, errors))
    return -int(errors or counts != success)


if __name__ == "__main__":
    import sys
    options = dict(debug=False)
    argv = list(sys.argv)
    if '--debug' in argv:
        options.update(debug=True)
        argv.remove('--debug')
    exit(test_ziplus(**options))
