from pygments.regexopt import regex_opt
import pygments.lexers._lilypond_builtins as _lilypond_builtins
import pygments.lexers._scheme_builtins as _scheme_builtins
import re
from textwrap import dedent

# \include and \version are actually handled by LilyPond’s lexer as a preprocessing step.
for keyword in ["include", "version"]:
    _lilypond_builtins.keywords.remove(keyword)
# \inherit-acceptability and \language are actually music functions.
for keyword in ["inherit-acceptability", "language"]:
    _lilypond_builtins.keywords.remove(keyword)
# Add keywords that are not treated as such in Pygments.
keywords = [
    "alternative",
    "change",
    "override",
    "repeat",
    "revert",
    "set",
    "tempo",
    "unset",
]
_lilypond_builtins.keywords.extend(keywords)
_lilypond_builtins.keywords.extend(
    [
        "default",
        "lyrics",
        "markup",
        "markuplist",
        "rest",
        "sequential",
        "simultaneous",
    ]
)

# Remove clefs that must be expressed as strings.
_lilypond_builtins.clefs = [
    clef for clef in _lilypond_builtins.clefs if not re.search(r"\d", clef)
]

# Remove keywords from music functions.
for keyword in keywords:
    _lilypond_builtins.music_functions.remove(keyword)

# Combine music commands, articulations, and dynamics.
music_objects = set(_lilypond_builtins.music_commands)
music_objects.update(_lilypond_builtins.articulations)
music_objects.update(_lilypond_builtins.dynamics)
# Remove punctuation marks.
for item in ["!", "(", ")", "-", "<", ">", "[", "]", "^", "|", "~"]:
    music_objects.remove(item)

# Remove keywords from markup commands.
for keyword in ["markup", "markuplist", "override", "score"]:
    _lilypond_builtins.markup_commands.remove(keyword)

with open("queries/highlights-builtins.scm", "w") as file:
    backslash_prefix = r"^\\\\"
    for list_and_selector in [
        (_lilypond_builtins.keywords, "keyword"),
        (_lilypond_builtins.music_functions, "function"),
        (music_objects, "constants.builtin"),
        (_lilypond_builtins.markup_commands, "function.markup"),
    ]:
        file.write(
            dedent(
                f'''\
        (
          (escaped_word) @{list_and_selector[1]}
          (#match? @{list_and_selector[1]} "{regex_opt(list_and_selector[0], backslash_prefix, '$').replace('\\-', '-')}")
        )

        '''
            )
        )

    for list_and_selector in [
        (_lilypond_builtins.grobs, "constant"),
        (_lilypond_builtins.contexts, "constant"),
        (_lilypond_builtins.translators, "constant"),
        (_lilypond_builtins.context_properties, "constant"),
    ]:
        file.write(
            dedent(
                f"""\
        (
          (symbol) @{list_and_selector[1]}
          (#match? @{list_and_selector[1]} "{regex_opt(list_and_selector[0], '^', '$')}")
        )

        """
            )
        )

    file.write(
        dedent(
            f"""\
    (
      (
        (escaped_word) @function
        (#match? @function "^\\\\\\\\tweak$")
      )
      .
      (
        (symbol) @label
        (#match? @label "{regex_opt(_lilypond_builtins.grob_properties, '^', '$')}")
      )
    )

    (property_expression
      (
        (symbol) @label 
        (#match? @label "{regex_opt(_lilypond_builtins.grob_properties, '^', '$')}")
      )
    )

    (
      (
        (escaped_word) @function
        (#match? @function "^\\\\\\\\clef$")
      )
      .
      (
        (symbol) @constant.clef
        (#match? @constant.clef "{regex_opt(_lilypond_builtins.clefs, '^', '$')}")
      )
    )

    (
      (
        (escaped_word) @function
        (#match? @function "^\\\\\\\\key$")
      )
      .
      (symbol)
      .
      (
        (escaped_word) @constant
        (#match? @constant  "{regex_opt(_lilypond_builtins.scales, backslash_prefix, '$')}")
      )
    )

    (
      (
        (escaped_word) @function
        (#match? @function "^\\\\\\\\repeat$")
      )
      .
      (
        (symbol) @constant
        (#match? @constant "{regex_opt(_lilypond_builtins.repeat_types, '^', '$')}")
      )
    )

    (
      (
        (escaped_word) @keyword
        (#match? @keyword "^\\\\\\\\paper$")
      )
      .
      (expression_block
        (
          (escaped_word) @iconstant
          (#match? @constant "{regex_opt(_lilypond_builtins.units, backslash_prefix, '$')}")
        )
      )
    )

    (
      (
        (escaped_word) @keyword
        (#match? @keyword "^\\\\\\\\chordmode$")
      )
      .
      (expression_block
        (
          (symbol) @keyword.operator
          (#match? @keyword.operator "{regex_opt(_lilypond_builtins.chord_modifiers, '^', '$')}")
        )
      )
    )

    (
      (
        (escaped_word) @function
        (#match? @function "^\\\\\\\\language$")
      )
      .
      (
        (symbol) @constant
        (#match? @constant "{regex_opt(_lilypond_builtins.pitch_language_names, '^', '$')}")
      )
    )

    (
      (
        (escaped_word) @keyword
        (#match? @keyword "^\\\\\\\\paper$")
      )
      .
      (expression_block
        (assignment_lhs
          [
            (
              (symbol) @variable
              (#match? @variable "{regex_opt(_lilypond_builtins.paper_variables, '^', '$')}")
            )

            (property_expression
              (
                (symbol) @variable
                (#match? @variable "{regex_opt(_lilypond_builtins.paper_variables, '^', '$')}")
              )
            )
          ]
        )
      )
    )

    (
      (
        (escaped_word) @keyword
        (#match? @keyword "^\\\\\\\\paper$")
      )
      .
      (expression_block
        (
          (escaped_word) @variable
          (#match? @variable "{regex_opt(_lilypond_builtins.paper_variables, backslash_prefix, '$')}")
        )
      )
    )

    (
      (
        (escaped_word) @keyword
        (#match? @keyword "^\\\\\\\\header$")
      )
      .
      (expression_block
        (assignment_lhs
          (symbol) @variable
          (#match? @variable "{regex_opt(_lilypond_builtins.header_variables, '^', '$')}")
        )
      )
    )
    """
        )
    )

with open("queries/highlights-scheme-builtins.scm", "w") as file:
    regex = re.sub(
        r"\\(.)",
        r"\\\\\1",
        regex_opt(_scheme_builtins.scheme_keywords, "^", "$").replace("\\-", "-"),
    )
    file.write(
        dedent(
            f"""\
    (
      (scheme_symbol) @keyword
      (#match? @keyword "{regex}")
    )
    """
        )
    )

    # Remove operator-like functions.
    for item in ["*", "+", "-", "/", "<", "<=", "=", ">", ">="]:
        _scheme_builtins.scheme_builtins.remove(item)
    regex = re.sub(
        r"\\(.)",
        r"\\\\\1",
        regex_opt(_scheme_builtins.scheme_builtins, "^", "$").replace("\\-", "-"),
    )
    file.write(
        dedent(
            f"""\
    (
      (scheme_symbol) @function
      (#match? @function "{regex}")
    )
    """
        )
    )

with open("queries/highlights-lilypond-builtins.scm", "w") as file:
    regex = re.sub(
        r"\\(.)",
        r"\\\\\1",
        regex_opt(_lilypond_builtins.scheme_functions, "^", "$").replace("\\-", "-"),
    )
    file.write(
        dedent(
            f"""\
    (
      (scheme_symbol) @function
      (#match? @function "{regex}")
    )
    """
        )
    )
