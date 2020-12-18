"""A Scheme interpreter and its read-eval-print loop."""
from __future__ import print_function  # Python 2 compatibility

import sys
import os

from scheme_builtins import *
from scheme_reader import *
from ucb import main, trace

##############
# Eval/Apply #
##############


def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in environment ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # PROBLEM 2
    if expr is None:
        return None
    if scheme_atomp(expr):
        if scheme_symbolp(expr):
            return env.lookup(expr)
        else:
            return expr
    elif scheme_listp(expr):
        first, rest = expr.first, expr.rest
        if scheme_symbolp(first) and first in SPECIAL_FORMS:
            return SPECIAL_FORMS[first](rest, env)
        else:
            eval_procedure = scheme_eval(expr.first, env)
            eval_args = expr.rest.map(lambda x: scheme_eval(x, env))
            return scheme_apply(eval_procedure, eval_args, env)
    else:
        #print("DEBUG:", "here")
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV."""
    # PROBLEM 2
    validate_procedure(procedure)
    if isinstance(procedure, BuiltinProcedure):
        return procedure.apply(args, env)
    elif isinstance(procedure, LambdaProcedure):
        new_frame = Frame(procedure.env)
        return procedure.apply(args, new_frame)
    elif isinstance(procedure, MuProcedure):
        new_frame = Frame(env)
        return procedure.apply(args, new_frame)


################
# Environments #
################


class Frame(object):
    """An environment frame binds Scheme symbols to Scheme values."""
    def __init__(self, parent):
        """An empty frame with parent frame PARENT (which may be None)."""
        "Your Code Here"
        self.parent = parent
        self.bindings = {}
        # Note: you should define instance variables self.parent and self.bindings

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        """Define Scheme SYMBOL to have VALUE."""
        self.bindings[symbol] = value

    # BEGIN PROBLEM 2/3
    "*** YOUR CODE HERE ***"

    def lookup(self, symbol):
        if symbol in self.bindings.keys():
            return self.bindings[symbol]
        elif self.parent != None:
            return self.parent.lookup(symbol)
        raise SchemeError('no symbol {0} in frame'.format(symbol))

    # END PROBLEM 2/3


##############
# Procedures #
##############


class Procedure(object):
    """The supertype of all Scheme procedures."""


def scheme_procedurep(x):
    return isinstance(x, Procedure)


class BuiltinProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""
    def __init__(self, fn, use_env=False, name='builtin'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4
        """
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        args_py = []
        while args != nil:
            args_py.append(args.first)
            args = args.rest
        if self.use_env:
            args_py.append(env)
        try:
            return self.fn(*args_py)
        except TypeError:
            raise SchemeError

        # END PROBLEM 2


class LambdaProcedure(Procedure):
    """A procedure defined by a lambda expression or a define form."""
    def __init__(self, formals, body, env):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env

    # BEGIN PROBLEM 3
    "*** YOUR CODE HERE ***"

    def apply(self, args, env):
        params = self.formals
        while args != nil:
            env.define(params.first, args.first)
            params = params.rest
            args = args.rest
        try:
            func_body = self.body
            ret = nil
            while func_body != nil:
                ret = scheme_eval(func_body.first, env)
                func_body = func_body.rest
            return ret
        except TypeError:
            raise SchemeError

    # END PROBLEM 3
    def __str__(self):
        return str(Pair('lambda', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(repr(self.formals),
                                                       repr(self.body),
                                                       repr(self.env))


def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, BuiltinProcedure(fn, name=proc_name))


#################
# Special Forms #
#################
"""
How you implement special forms is up to you. We recommend you encapsulate the
logic for each special form separately somehow, which you can do here.
"""

# BEGIN PROBLEM 2/3
"*** YOUR CODE HERE ***"


def do_define_form(expressions, env):
    validate_form(expressions, 2)
    target = expressions.first
    if scheme_symbolp(target):
        validate_form(expressions, 2, 2)
        env.define(target, scheme_eval(expressions.rest.first, env))
        return target
    elif isinstance(target, Pair) and scheme_symbolp(target.first):
        formals = target.rest
        validate_formals(formals)
        body = expressions.rest
        validate_form(body, 1)
        lambda_procedure = LambdaProcedure(formals, body, env)
        env.define(target.first, lambda_procedure)
        return target.first
    else:
        bad_target = target.first if isinstance(target, Pair) else target
        raise SchemeError('non-symbol: {0}'.format(bad_target))


def do_if_form(expressions, env):
    validate_form(expressions, 3, 3)
    predicate = scheme_eval(expressions.first, env)

    if is_true_primitive(predicate):
        return scheme_eval(expressions.rest.first, env)
    else:
        return scheme_eval(expressions.rest.rest.first, env)


def do_quote_form(expressions, env):
    validate_form(expressions, 1, 1)
    if expressions.rest == nil:
        return expressions.first
    return expressions


def do_lambda_form(expressions, env):
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    body = expressions.rest
    validate_form(body, 1)
    return LambdaProcedure(formals, body, env)


def do_mu_form(expressions, env):
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    body = expressions.rest
    validate_form(body, 1)
    return MuProcedure(formals, body)


def do_begin_form(expressions, env):
    ret = None
    while expressions != nil:
        ret = scheme_eval(expressions.first, env)
        expressions = expressions.rest
    return ret


def do_and_form(expressions, env):
    test = expressions
    ret = True
    while test != nil:
        ret = scheme_eval(test.first, env)
        if is_false_primitive(ret):
            return ret
        test = test.rest
    return ret


def do_or_form(expressions, env):
    test = expressions
    ret = False
    while test != nil:
        ret = scheme_eval(test.first, env)
        if is_true_primitive(ret):
            return ret
        test = test.rest
    return ret


def do_cond_form(expressions, env):
    validate_form(expressions, 1)

    while expressions != nil:
        clause = expressions.first
        test = clause.first
        subexpression = clause.rest
        if test == 'else':
            ret = True
            while subexpression != nil:
                ret = scheme_eval(subexpression.first, env)
                subexpression = subexpression.rest
            return ret
        else:
            val = scheme_eval(test, env)
            if is_true_primitive(val):
                ret = val
                while subexpression != nil:
                    ret = scheme_eval(subexpression.first, env)
                    subexpression = subexpression.rest
                return ret
            else:
                expressions = expressions.rest
    return None


def do_let_form(expressions, env):
    validate_form(expressions, 2)
    binding = expressions.first
    body = expressions.rest
    validate_form(binding, 1)

    new_frame = Frame(env)
    while binding != nil:
        each_binding = binding.first
        name = each_binding.first
        if not scheme_symbolp(name):
            raise SchemeError('non-symbol: {0}'.format(name))
        validate_form(each_binding.rest, 1, 1)
        val = scheme_eval(each_binding.rest.first, env)
        new_frame.define(name, val)
        binding = binding.rest
    ret = None
    while body != nil:
        ret = scheme_eval(body.first, new_frame)
        body = body.rest
    return ret


SPECIAL_FORMS = {
    'define': do_define_form,
    'if': do_if_form,
    'quote': do_quote_form,
    'lambda': do_lambda_form,
    'begin': do_begin_form,
    'and': do_and_form,
    'or': do_or_form,
    'cond': do_cond_form,
    'let': do_let_form,
    'mu': do_mu_form
}
# END PROBLEM 2/3

# Utility methods for checking the structure of Scheme programs


def validate_form(expr, min, max=float('inf')):
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.

    >>> validate_form(read_line('(a b)'), 2)
    """
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + repl_str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')


def validate_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbolhase I of the project will be similar to the standard version, buts
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a list of symbols or if any symbol is repeated.

    >>> validate_formals(read_line('(a b c)'))
    """
    symbols = set()

    def validate_and_add(symbol, is_last):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        validate_and_add(formals.first, formals.rest is nil)
        formals = formals.rest

    # here for compatibility with DOTS_ARE_CONS
    if formals != nil:
        validate_and_add(formals, True)


def validate_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), repl_str(procedure)))


#################
# Dynamic Scope #
#################


class MuProcedure(Procedure):
    """A procedure defined by a mu expression, which has dynamic scope.
     _________________
    < Scheme is cool! >
     -----------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    """
    def __init__(self, formals, body):
        """A procedure with formal parameter list FORMALS (a Scheme list) and
        Scheme list BODY as its definition."""
        self.formals = formals
        self.body = body

    def apply(self, args, env):
        params = self.formals
        while args != nil:
            env.define(params.first, args.first)
            params = params.rest
            args = args.rest
        try:
            func_body = self.body
            ret = nil
            while func_body != nil:
                ret = scheme_eval(func_body.first, env)
                func_body = func_body.rest
            return ret
        except TypeError:
            raise SchemeError

    def __str__(self):
        return str(Pair('mu', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'MuProcedure({0}, {1})'.format(repr(self.formals),
                                              repr(self.body))


##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here?


def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not a Thunk.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the optional questions."""
    val = scheme_apply(procedure, args, env)
    # Add stuff here?
    return val


# BEGIN PROBLEM 8
"*** YOUR CODE HERE ***"
# END PROBLEM 8

####################
# Extra Procedures #
####################


def scheme_map(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'map')
    validate_type(s, scheme_listp, 1, 'map')
    return s.map(lambda x: complete_apply(fn, Pair(x, nil), env))


def scheme_filter(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'filter')
    validate_type(s, scheme_listp, 1, 'filter')
    head, current = nil, nil
    while s is not nil:
        item, s = s.first, s.rest
        if complete_apply(fn, Pair(item, nil), env):
            if head is nil:
                head = Pair(item, nil)
                current = head
            else:
                current.rest = Pair(item, nil)
                current = current.rest
    return head


def scheme_reduce(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'reduce')
    validate_type(s, lambda x: x is not nil, 1, 'reduce')
    validate_type(s, scheme_listp, 1, 'reduce')
    value, s = s.first, s.rest
    while s is not nil:
        value = complete_apply(fn, scheme_list(value, s.first), env)
        s = s.rest
    return value


################
# Input/Output #
################


def read_eval_print_loop(next_line,
                         env,
                         interactive=False,
                         quiet=False,
                         startup=False,
                         load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError)
                    and 'maximum recursion depth exceeded' not in getattr(
                        err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            print()
            return


def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into environment ENV,
    with verbosity determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    validate_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines, )

    def next_line():
        return buffer_lines(*args)

    read_eval_print_loop(next_line, env, quiet=quiet)


def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))


def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define('eval', BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply', BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('load', BuiltinProcedure(scheme_load, True, 'load'))
    env.define('procedure?',
               BuiltinProcedure(scheme_procedurep, False, 'procedure?'))
    env.define('map', BuiltinProcedure(scheme_map, True, 'map'))
    env.define('filter', BuiltinProcedure(scheme_filter, True, 'filter'))
    env.define('reduce', BuiltinProcedure(scheme_reduce, True, 'reduce'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env


@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
    parser.add_argument(
        '--pillow-turtle',
        action='store_true',
        help=
        'run with pillow-based turtle. This is much faster for rendering but there is no GUI'
    )
    parser.add_argument('--turtle-save-path',
                        default=None,
                        help='save the image to this location when done')
    parser.add_argument('-load',
                        '-i',
                        action='store_true',
                        help='run file interactively')
    parser.add_argument('file',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=None,
                        help='Scheme file to run')
    args = parser.parse_args()

    import scheme
    scheme.TK_TURTLE = not args.pillow_turtle
    scheme.TURTLE_SAVE_PATH = args.turtle_save_path
    sys.path.insert(0, '')
    sys.path.append(
        os.path.dirname(os.path.abspath(os.path.dirname(scheme.__file__))))

    next_line = buffer_input
    interactive = True
    load_files = []

    if args.file is not None:
        if args.load:
            load_files.append(getattr(args.file, 'name'))
        else:
            lines = args.file.readlines()

            def next_line():
                return buffer_lines(lines)

            interactive = False

    read_eval_print_loop(next_line,
                         create_global_frame(),
                         startup=True,
                         interactive=interactive,
                         load_files=load_files)
    tscheme_exitonclick()