# Import argparse to parse command-line arguments.
import argparse
# Import Path for filesystem path handling.
from pathlib import Path

# Import compiler and its custom error type.
from compiler import Compiler, CompilerError
# Import parser and its custom error type.
from parser import Parser, ParserError
# Import lexer and its custom error type.
from tokenizer import Lexer, LexerError


# Define a helper to remove a leading shebang line from source.
def _strip_shebang(source: str) -> str:
    # Check whether source starts with shebang characters.
    if source.startswith("#!"):
        # Find the first newline after the shebang line.
        i = source.find("\n")
        # Return empty if file is only shebang, otherwise slice after first newline.
        return "" if i == -1 else source[i + 1 :]
    # Return source unchanged when there is no shebang.
    return source


# Define the main CLI entry point.
def main() -> None:
    # Create an argument parser with a short description.
    parser = argparse.ArgumentParser(description="Run a .memecode file.")
    # Add required positional argument for the input file path.
    parser.add_argument("file", type=Path, help="Path to file.memecode")
    # Parse command-line arguments from the shell invocation.
    args = parser.parse_args()

    # Validate the expected input extension.
    if args.file.suffix != ".memecode":
        # Exit with a friendly message when extension is invalid.
        raise SystemExit("Use a .memecode file.")
    # Validate that the file actually exists.
    if not args.file.exists():
        # Exit with a not-found message when file is missing.
        raise SystemExit(f"Not found: {args.file}")

    # Read file contents and strip an optional shebang line.
    source = _strip_shebang(args.file.read_text(encoding="utf-8"))

    # Start compilation pipeline with error handling.
    try:
        # Tokenize source text into lexical tokens.
        lexer = Lexer(source)
        # Produce token list from the lexer.
        tokens = lexer.tokenize()
        # Parse tokens into an AST.
        parsed = Parser(tokens).parse()
        # Compile AST into executable Python code.
        code = Compiler().compile(parsed)
    # Catch language pipeline errors and convert to clean CLI exit.
    except (LexerError, ParserError, CompilerError) as e:
        # Exit with prefixed error message while keeping original exception context.
        raise SystemExit(f"Error: {e}") from e

    # Execute generated Python code in a controlled global namespace.
    exec(
        # Provide compiled code string to exec.
        code,
        # Set minimal globals that emulate script execution context.
        {"__name__": "__main__", "__file__": str(args.file.resolve())},
    )


# Run main only when file is executed as a script.
if __name__ == "__main__":
    # Invoke CLI entry point.
    main()
