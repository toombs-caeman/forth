an exploration of the Forth programming language

# good ideas
* elmyras - generic stack reordering operator (up to 9 deep)
    * freeze - freeze program state into executable binary
    * munge - stack re-order operations
    * `-01` (a b -- b a)
    * `-012` (a b c -- c b a)
    * the problem with this is how do you drop deeply
    * proposal 'munge'
        * `0:`
        * `3~011` (a b c d -- d c c)
        * `0~` (a -- ) equivalent to drop
        * `~` or `~0` identity function
        * `0~111` (a b -- a a a a)
        * `{left}~{right}` left if given is the stack depth to drop. right if given is a list of (pre-op) indexes to push (post-drop)
```
def munge(key:str, f:'Forth'):
    """a stack re-ordering operator to replace dup, drop and others."""
    left, right = key.split(':')
    f.d[-int(left or '1'):] = (f.d[-1-int(d)] for d in right)
```
* provide own language server (lsp) as a word?
* bootstrap
    * non-portable assembly
    * non-portable forth
    * portable forth

* scopes/imports - heaps are dicts, with cascades.
    * words: :, undef, scope, unscope, ;
    * words: pyload, load, eval, import
* nice foreign function interface, with inspect?
    * auto-pop args?
    * wrap zero arg functions to drop forth param
* prompt_toolkit
    * syntax highlighting
    * output highlighting
* turtle forth

#
is it possible to run a forth kernel (even very slowly) on a GPU?

# ref
https://github.com/jdinunzio/pyforth/tree/master
https://github.com/nornagon/jonesforth
https://www.forth.com/wp-content/uploads/2018/11/thinking-forth-color.pdf
https://github.com/toombs-caeman/treerat
