import json
import sys

# MemeCode words
KEYWORDS = [
    "yapping",
    "lore",
    "sixSeven",
    "vibeCheck",
    "losing5050",
    "noCap",
    "cap",
    "bet",
    "lowkey",
    "nahFr",
]

# Allowed variable type keywords
TYPE_KEYWORDS = ["lore", "sixSeven", "vibeCheck", "losing5050"]

# Operators with 2 characters
DOUBLE_OPERATORS = {
    "==": "EQ_EQ",
    "!=": "NE",
    "<=": "LE",
    ">=": "GE",
    "&&": "AND",
    "||": "OR",
}

# Operators with 1 character
SINGLE_OPERATORS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "=": "EQUALS",
    "<": "LT",
    ">": "GT",
}


def read_program(file_path):
    with open(file_path, "r") as file:
        return file.read()


def lexer(source_text):
    tokens = []
    i = 0

    while i < len(source_text):
        ch = source_text[i]

        # Skip spaces, tabs, and new lines
        if ch in " \t\n\r":
            i += 1
            continue

        # Skip comments: # until end of line
        if ch == "#":
            while i < len(source_text) and source_text[i] != "\n":
                i += 1
            continue

        # Check 2-character operators first
        if i + 1 < len(source_text):
            two = source_text[i : i + 2]
            if two in DOUBLE_OPERATORS:
                tokens.append({"type": DOUBLE_OPERATORS[two], "value": two})
                i += 2
                continue

        # Check 1-character operators
        if ch in SINGLE_OPERATORS:
            tokens.append({"type": SINGLE_OPERATORS[ch], "value": ch})
            i += 1
            continue

        # Strings: "hello" or 'hello'
        if ch == '"' or ch == "'":
            quote = ch
            i += 1
            start = i
            while i < len(source_text) and source_text[i] != quote:
                i += 1

            if i >= len(source_text):
                raise SyntaxError("String was not closed.")

            tokens.append({"type": "STRING", "value": source_text[start:i]})
            i += 1
            continue

        # Numbers: int or float
        if ch.isdigit():
            start = i
            has_dot = False
            while i < len(source_text) and (
                source_text[i].isdigit() or source_text[i] == "."
            ):
                if source_text[i] == ".":
                    has_dot = True
                i += 1

            number_text = source_text[start:i]
            if has_dot:
                tokens.append({"type": "FLOAT", "value": float(number_text)})
            else:
                tokens.append({"type": "INT", "value": int(number_text)})
            continue

        # Identifier or keyword
        if ch.isalpha() or ch == "_":
            start = i
            while i < len(source_text) and (
                source_text[i].isalnum() or source_text[i] == "_"
            ):
                i += 1

            word = source_text[start:i]
            if word in KEYWORDS:
                tokens.append({"type": "KEYWORD", "value": word})
            else:
                tokens.append({"type": "IDENTIFIER", "value": word})
            continue

        raise ValueError("Unexpected character: " + ch)

    return tokens


def parse(tokens):
    position = 0
    program_node = {"type": "Program", "body": []}

    while position < len(tokens):
        token = tokens[position]

        # Variable declaration: TYPE name = expression
        if token["type"] == "KEYWORD" and token["value"] in TYPE_KEYWORDS:
            var_type = tokens[position]["value"]
            position += 1

            var_name = tokens[position]["value"]
            position += 1

            # skip =
            position += 1

            value_node, position = parse_expression(tokens, position)

            program_node["body"].append(
                {
                    "type": "VariableDeclaration",
                    "var_type": var_type,
                    "name": var_name,
                    "value": value_node,
                }
            )
            continue

        # Print statement: yapping(expression)
        if token["type"] == "KEYWORD" and token["value"] == "yapping":
            position += 1
            if tokens[position]["type"] != "LPAREN":
                raise SyntaxError("Expected '(' after yapping")
            position += 1

            value_node, position = parse_expression(tokens, position)

            if position >= len(tokens) or tokens[position]["type"] != "RPAREN":
                raise SyntaxError("Expected ')' after yapping expression")
            position += 1

            program_node["body"].append({"type": "PrintStatement", "value": value_node})
            continue

        # If statement: bet condition { ... } lowkey condition { ... } nahFr { ... }
        if token["type"] == "KEYWORD" and token["value"] == "bet":
            position += 1
            condition_node, position = parse_expression(tokens, position)

            # skip {
            position += 1

            if_body = []
            while tokens[position]["type"] != "RBRACE":
                statement_node, position = parse_statement_in_block(tokens, position)
                if_body.append(statement_node)

            # skip }
            position += 1

            if_node = {
                "type": "IfStatement",
                "condition": condition_node,
                "body": if_body,
                "elseif_branches": [],
                "else_body": None,
            }

            # zero or many else-if branches
            while (
                position < len(tokens)
                and tokens[position]["type"] == "KEYWORD"
                and tokens[position]["value"] == "lowkey"
            ):
                position += 1
                elseif_condition, position = parse_expression(tokens, position)

                # skip {
                position += 1

                elseif_body = []
                while tokens[position]["type"] != "RBRACE":
                    statement_node, position = parse_statement_in_block(tokens, position)
                    elseif_body.append(statement_node)

                # skip }
                position += 1
                if_node["elseif_branches"].append(
                    {"condition": elseif_condition, "body": elseif_body}
                )

            # optional else branch
            if (
                position < len(tokens)
                and tokens[position]["type"] == "KEYWORD"
                and tokens[position]["value"] == "nahFr"
            ):
                position += 1
                # skip {
                position += 1

                else_body = []
                while tokens[position]["type"] != "RBRACE":
                    statement_node, position = parse_statement_in_block(tokens, position)
                    else_body.append(statement_node)

                # skip }
                position += 1
                if_node["else_body"] = else_body

            program_node["body"].append(if_node)
            continue

        raise ValueError("Syntax error near token index " + str(position))

    return program_node


def parse_statement_in_block(tokens, position):
    token = tokens[position]

    if token["type"] == "KEYWORD" and token["value"] in TYPE_KEYWORDS:
        var_type = tokens[position]["value"]
        position += 1
        var_name = tokens[position]["value"]
        position += 1
        # skip =
        position += 1
        value_node, position = parse_expression(tokens, position)
        return (
            {
                "type": "VariableDeclaration",
                "var_type": var_type,
                "name": var_name,
                "value": value_node,
            },
            position,
        )

    if token["type"] == "KEYWORD" and token["value"] == "yapping":
        position += 1
        if tokens[position]["type"] != "LPAREN":
            raise SyntaxError("Expected '(' after yapping")
        position += 1
        value_node, position = parse_expression(tokens, position)
        if position >= len(tokens) or tokens[position]["type"] != "RPAREN":
            raise SyntaxError("Expected ')' after yapping expression")
        position += 1
        return {"type": "PrintStatement", "value": value_node}, position

    raise ValueError("Syntax error in block near token index " + str(position))


def parse_expression(tokens, position):
    left_node, position = parse_primary(tokens, position)

    while position < len(tokens) and tokens[position]["type"] in [
        "AND",
        "OR",
        "EQ_EQ",
        "NE",
        "LT",
        "GT",
        "LE",
        "GE",
    ]:
        operator = tokens[position]["value"]
        position += 1
        right_node, position = parse_primary(tokens, position)
        left_node = {
            "type": "BinaryOp",
            "op": operator,
            "left": left_node,
            "right": right_node,
        }

    return left_node, position


def parse_primary(tokens, position):
    token = tokens[position]

    if token["type"] == "INT":
        return {"type": "Integer", "value": token["value"]}, position + 1

    if token["type"] == "FLOAT":
        return {"type": "Float", "value": token["value"]}, position + 1

    if token["type"] == "STRING":
        return {"type": "String", "value": token["value"]}, position + 1

    if token["type"] == "KEYWORD" and token["value"] == "noCap":
        return {"type": "Boolean", "value": True}, position + 1

    if token["type"] == "KEYWORD" and token["value"] == "cap":
        return {"type": "Boolean", "value": False}, position + 1

    if token["type"] == "IDENTIFIER":
        return {"type": "Identifier", "name": token["value"]}, position + 1

    raise ValueError("Unexpected token in expression: " + str(token))


def run_interpreter(ast):
    variables = {}

    def evaluate(node):
        node_type = node["type"]

        if node_type == "Integer":
            return node["value"]
        if node_type == "Float":
            return node["value"]
        if node_type == "String":
            return node["value"]
        if node_type == "Boolean":
            return node["value"]
        if node_type == "Identifier":
            return variables[node["name"]]

        if node_type == "BinaryOp":
            left_value = evaluate(node["left"])
            right_value = evaluate(node["right"])
            operator = node["op"]

            if operator == "==":
                return left_value == right_value
            if operator == "!=":
                return left_value != right_value
            if operator == "<":
                return left_value < right_value
            if operator == ">":
                return left_value > right_value
            if operator == "<=":
                return left_value <= right_value
            if operator == ">=":
                return left_value >= right_value
            if operator == "&&":
                return left_value and right_value
            if operator == "||":
                return left_value or right_value

        raise ValueError("Unknown node type: " + node_type)

    def execute(statement):
        if statement["type"] == "VariableDeclaration":
            variables[statement["name"]] = evaluate(statement["value"])
            return

        if statement["type"] == "PrintStatement":
            print(evaluate(statement["value"]))
            return

        if statement["type"] == "IfStatement":
            if evaluate(statement["condition"]):
                for inner_statement in statement["body"]:
                    execute(inner_statement)
                return

            did_run_branch = False
            for branch in statement["elseif_branches"]:
                if evaluate(branch["condition"]):
                    for inner_statement in branch["body"]:
                        execute(inner_statement)
                    did_run_branch = True
                    break

            if not did_run_branch and statement["else_body"]:
                for inner_statement in statement["else_body"]:
                    execute(inner_statement)
            return

        raise ValueError("Unknown statement type: " + statement["type"])

    for statement in ast["body"]:
        execute(statement)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Please provide a source file. Example: python interpreter_beginner.py example.memecode")

    source_file = sys.argv[1]
    source_code = read_program(source_file)
    token_list = lexer(source_code)
    ast_tree = parse(token_list)

    print("--------------AST--------------")
    print(json.dumps(ast_tree, indent=2))
    print("\n--------------OUTPUT--------------")
    run_interpreter(ast_tree)
