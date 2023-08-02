# `ProcessWrapper` Class
## Table Indirection Feature
When the table is not at a static location in memory,
`ProcessWrapper` provides a way to dynamically decide where to read the table from.

This is done by specifying the `table_indirection: TableIndirection` parameter in the `ProcessWrapper`
constructor.

The options are:
* `StaticTableIndirection` - this is the default option (so there is no indirection) and the table will be read from
    `start_addr`.
* `PointerTableIndirection` - this means `start_addr` now refers to the address of a pointer
    which points at where the table is.
* `HookTableIndirection` - this means the process will be run with an injector which will create
    a hook on `malloc` and prints the allocations to `Trace Log File`.
    The user also specifies how to select which of these allocations should be treated as the creation
    of the table pointer.
    For example the user can pass to the `ProcessWrapper` constructor the parameter:
    `table_indirection=HookTableIndirection.create_idx_match(3)` which means the 4'th
    allocation will be treated as the table pointer.


# Internal Convensions
## Trace Log File Format
The hooking trace log file will be named `trace_dll_log.txt`
The file will have the format:
```
[pid]
[malloc addr] [malloc size]
[malloc addr] [malloc size]
[malloc addr] [malloc size]
...
```

Here all of the values are in hex format with prefix `0x`.
The first `[malloc addr] [malloc size]` is for the first malloc hooked etc.
For example:
```
0x7f23
0x603fb0 0x2
0x602fb0 0x10
0x603ff0 0x200
```