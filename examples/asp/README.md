# Spliced to print Asp

This is an example of using spliced just to print asp facts to the terminal,
which is an easy thing it can do! We start with [smeagle-output.json](smeagle-output.json),
load it, and then use the same SmeagleRunner to print facts to the terminal.

```pythonb
import spliced.utils as utils
import spliced.predict.smeagle as smeagle

cli = smeagle.SmeagleRunner()
data = utils.read_json("smeagle-output.json")

# We can accept a path (will run smeagle) or the raw data, so
# it is important to provide a kwarg here!
cli.generate_facts(data=data)
```
```bash
%============================================================================
% Library Facts
%============================================================================

%----------------------------------------------------------------------------
% Library: libtest.so
%----------------------------------------------------------------------------
abi_typelocation("libtest.so","_Z7bigcallllllln","a","Integer","%rdi","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","b","Integer","%rsi","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","c","Integer","%rdx","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","d","Integer","%rcx","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","e","Integer","%r8","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","f","Integer","framebase+8","import","0").
```

This is provided in a little [generate-facts.py](generate-facts.py) courtesy script.

```bash
$ python generate-facts.py smeagle-output.json
```
```bash
%============================================================================
% Library Facts
%============================================================================

%----------------------------------------------------------------------------
% Library: libtest.so
%----------------------------------------------------------------------------
abi_typelocation("libtest.so","_Z7bigcallllllln","a","Integer","%rdi","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","b","Integer","%rsi","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","c","Integer","%rdx","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","d","Integer","%rcx","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","e","Integer","%r8","import","0").
abi_typelocation("libtest.so","_Z7bigcallllllln","f","Integer","framebase+8","import","0").
```
