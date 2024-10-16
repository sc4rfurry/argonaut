# /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import List, Any
import sys
from pathlib import Path


def generate_completion_script(shell: str, parser: Any) -> str:
    if shell == "bash":
        return _generate_bash_completion(parser)
    elif shell == "zsh":
        return _generate_zsh_completion(parser)
    elif shell == "fish":
        return _generate_fish_completion(parser)
    elif shell == "powershell":
        return _generate_powershell_completion(parser)
    else:
        raise ValueError(f"Unsupported shell: {shell}")


def _generate_bash_completion(parser: Any) -> str:
    script = f"""
_argonaut_completion()
{{
    local cur prev opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    opts="{' '.join(_get_all_options(parser))}"
    subcommands="{' '.join(parser.subcommands.keys())}"

    if [[ ${{cur}} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
        return 0
    fi

    case "${{prev}}" in
{_generate_option_cases(parser)}
    esac

    if [[ ${{COMP_CWORD}} -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${{subcommands}}" -- ${{cur}}) )
        return 0
    fi

    COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
    return 0
}}

complete -F _argonaut_completion {os.path.basename(sys.argv[0])}
"""
    return script


def _generate_zsh_completion(parser: Any) -> str:
    script = f"""
#compdef {os.path.basename(sys.argv[0])}

_argonaut_completion() {{
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments \\
        {_generate_zsh_arguments(parser)}
}}

_argonaut_completion "$@"
"""
    return script


def _generate_fish_completion(parser: Any) -> str:
    script = f"""
function __fish_argonaut_no_subcommand
    set cmd (commandline -opc)
    if [ (count $cmd) -eq 1 ]
        return 0
    end
    return 1
end

{_generate_fish_options(parser)}

{_generate_fish_subcommands(parser)}
"""
    return script


def _generate_powershell_completion(parser: Any) -> str:
    script = f"""
Register-ArgumentCompleter -Native -CommandName {Path(sys.argv[0]).name} -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)
    $opts = @({', '.join(f"'{opt}'" for opt in _get_all_options(parser))})
    $opts | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }}
}}
"""
    return script


def _get_all_options(parser: Any) -> List[str]:
    options = []
    for arg in parser.arguments:
        options.extend([name for name in arg.names if name.startswith("-")])
    return options


def _generate_option_cases(parser: Any) -> str:
    cases = ""
    for arg in parser.arguments:
        if arg.choices:
            cases += f"        {arg.names[0]})\n"
            cases += f"            COMPREPLY=( $(compgen -W \"{' '.join(arg.choices)}\" -- ${{cur}}) )\n"
            cases += "            return 0\n"
            cases += "            ;;\n"
    return cases


def _generate_zsh_arguments(parser: Any) -> str:
    args = []
    for arg in parser.arguments:
        arg_str = f"'{arg.names[0]}[{arg.help}]"
        if arg.choices:
            arg_str += f":({' '.join(arg.choices)})"
        arg_str += "'"
        args.append(arg_str)
    return " \\\n        ".join(args)


def _generate_fish_options(parser: Any) -> str:
    options = ""
    for arg in parser.arguments:
        options += f"complete -c {os.path.basename(sys.argv[0])} -n '__fish_argonaut_no_subcommand' -l {arg.names[0][2:]} -d '{arg.help}'\n"
    return options


def _generate_fish_subcommands(parser: Any) -> str:
    subcommands = ""
    for name, subcommand in parser.subcommands.items():
        subcommands += f"complete -c {os.path.basename(sys.argv[0])} -n '__fish_argonaut_no_subcommand' -a {name} -d '{subcommand.description}'\n"
    return subcommands
