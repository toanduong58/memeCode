import sys
import json

filename = sys.argv[1]

# MemeCode keywords
KEYWORDS = ["yapping", "lore", "sixSeven", "vibeCheck", "losing5050", "noCap", "cap", "bet", "lowkey", "nahFr"]

def readProgram():
    full_prog = ""
    with open(filename, "r") as file:
        for line in file:
            full_prog += line
    return full_prog

def lexer(source):
    tokens = []
    currentPosition = 0
    
    while currentPosition < len(source):
        char = source[currentPosition]
        
        # Skip whitespace, tabs, and newlines (whitespace)
        if char in " \t\n\r":
            currentPosition += 1
            continue
        
        # Skip comments
        if char == "#":
            while currentPosition < len(source) and source[currentPosition] != "\n":
                currentPosition += 1
            continue
        
        # Two character operators (==, !=, <=, >=, &&, ||)
        if currentPosition + 1 < len(source):
            two = source[currentPosition:currentPosition+2]
            if two == "==":
                tokens.append({"type": "EQ_EQ", "value": "=="})
                currentPosition += 2
                continue
            if two == "!=":
                tokens.append({"type": "NE", "value": "!="})
                currentPosition += 2
                continue
            if two == "<=":
                tokens.append({"type": "LE", "value": "<="})
                currentPosition += 2
                continue
            if two == ">=":
                tokens.append({"type": "GE", "value": ">="})
                currentPosition += 2
                continue
            if two == "&&":
                tokens.append({"type": "AND", "value": "&&"})
                currentPosition += 2
                continue
            if two == "||":
                tokens.append({"type": "OR", "value": "||"})
                currentPosition += 2
                continue
        
        # Single character tokens
        if char == "(":
            tokens.append({"type": "LPAREN", "value": "("})
            currentPosition += 1
            continue
        if char == ")":
            tokens.append({"type": "RPAREN", "value": ")"})
            currentPosition += 1
            continue
        if char == "{":
            tokens.append({"type": "LBRACE", "value": "{"})
            currentPosition += 1
            continue
        if char == "}":
            tokens.append({"type": "RBRACE", "value": "}"})
            currentPosition += 1
            continue
        if char == "=":
            tokens.append({"type": "EQUALS", "value": "="})
            currentPosition += 1
            continue
        if char == "<":
            tokens.append({"type": "LT", "value": "<"})
            currentPosition += 1
            continue
        if char == ">":
            tokens.append({"type": "GT", "value": ">"})
            currentPosition += 1
            continue
        
        # Strings (both single and double quotes)
        if char == "'" or char == '"':
            quote_char = char
            currentPosition += 1
            start = currentPosition
            while currentPosition < len(source) and source[currentPosition] != quote_char:
                currentPosition += 1
            if currentPosition >= len(source):
                raise SyntaxError(f"Unterminated string starting with {quote_char}")
            tokens.append({"type": "STRING", "value": source[start:currentPosition]})
            currentPosition += 1
            continue
        
        # Numbers
        if char.isdigit():
            start = currentPosition
            has_dot = False
            while currentPosition < len(source) and (source[currentPosition].isdigit() or source[currentPosition] == "."):
                if source[currentPosition] == ".":
                    has_dot = True
                currentPosition += 1
            value = source[start:currentPosition]
            if has_dot:
                tokens.append({"type": "FLOAT", "value": float(value)})
            else:
                tokens.append({"type": "INT", "value": int(value)})
            continue
        
        # Identifiers and keywords
        if char.isalpha() or char == "_":
            start = currentPosition
            while currentPosition < len(source) and (source[currentPosition].isalnum() or source[currentPosition] == "_"):
                currentPosition += 1
            word = source[start:currentPosition]
            if word in KEYWORDS:
                tokens.append({"type": "KEYWORD", "value": word})
            else:
                tokens.append({"type": "IDENTIFIER", "value": word})
            continue
        
        raise ValueError("Unexpected character: " + char)
    
    return tokens

def parse(tokens):
    current = 0
    ast = {"type": "Program", "body": []}
    
    while current < len(tokens):
        
        # Variable declaration: TYPE IDENTIFIER = EXPR
        if (
            tokens[current]["type"] == "KEYWORD" and
            tokens[current]["value"] in ["lore", "sixSeven", "vibeCheck", "losing5050"]
        ):
            var_type = tokens[current]["value"]
            current += 1
            
            var_name = tokens[current]["value"]
            current += 1
            
            current += 1  # skip =
            
            # Parse value (can be number, string, boolean, identifier, or comparison)
            value_node, current = parse_expression(tokens, current)
            
            ast["body"].append({
                "type": "VariableDeclaration",
                "var_type": var_type,
                "name": var_name,
                "value": value_node
            })
        
        # Print statement: yapping(EXPR)
        elif (
            tokens[current]["type"] == "KEYWORD" and
            tokens[current]["value"] == "yapping"
        ):
            current += 1  # skip yapping
            if tokens[current]["type"] != "LPAREN":
                raise SyntaxError("Expected '(' after yapping")
            current += 1  # skip (
            
            value_node, current = parse_expression(tokens, current)
            
            if current >= len(tokens) or tokens[current]["type"] != "RPAREN":
                raise SyntaxError("Expected ')' to close yapping")
            current += 1  # skip )
            
            ast["body"].append({
                "type": "PrintStatement",
                "value": value_node
            })
        
        # If statement: bet EXPR { ... } else if EXPR { ... } else { ... }
        elif (
            tokens[current]["type"] == "KEYWORD" and
            tokens[current]["value"] == "bet"
        ):
            current += 1  # skip bet
            
            condition, current = parse_expression(tokens, current)
            
            current += 1  # skip {
            
            body = []
            while tokens[current]["type"] != "RBRACE":
                stmt, current = parse_statement_inside_block(tokens, current)
                body.append(stmt)
            
            current += 1  # skip }
            
            node = {
                "type": "IfStatement",
                "condition": condition,
                "body": body,
                "elseif_branches": [],
                "else_body": None
            }
            
            # Check for lowkey (else-if)
            while current < len(tokens) and tokens[current]["type"] == "KEYWORD" and tokens[current]["value"] == "lowkey":
                current += 1  # skip lowkey
                elif_cond, current = parse_expression(tokens, current)
                current += 1  # skip {
                elif_body = []
                while tokens[current]["type"] != "RBRACE":
                    stmt, current = parse_statement_inside_block(tokens, current)
                    elif_body.append(stmt)
                current += 1  # skip }
                node["elseif_branches"].append({"condition": elif_cond, "body": elif_body})
            
            # Check for nahFr (else)
            if current < len(tokens) and tokens[current]["type"] == "KEYWORD" and tokens[current]["value"] == "nahFr":
                current += 1  # skip nahFr
                current += 1  # skip {
                else_body = []
                while tokens[current]["type"] != "RBRACE":
                    stmt, current = parse_statement_inside_block(tokens, current)
                    else_body.append(stmt)
                current += 1  # skip }
                node["else_body"] = else_body
            
            ast["body"].append(node)
        
        else:
            raise ValueError("Syntax error near token " + str(current))
    
    return ast

def parse_statement_inside_block(tokens, current):
    # Variable declaration inside block
    if tokens[current]["type"] == "KEYWORD" and tokens[current]["value"] in ["lore", "sixSeven", "vibeCheck", "losing5050"]:
        var_type = tokens[current]["value"]
        current += 1
        var_name = tokens[current]["value"]
        current += 1
        current += 1  # skip =
        value_node, current = parse_expression(tokens, current)
        return {"type": "VariableDeclaration", "var_type": var_type, "name": var_name, "value": value_node}, current
    
    # Print inside block
    if tokens[current]["type"] == "KEYWORD" and tokens[current]["value"] == "yapping":
        current += 1  # skip yapping
        if tokens[current]["type"] != "LPAREN":
            raise SyntaxError("Expected '(' after yapping")
        current += 1  # skip (
        value_node, current = parse_expression(tokens, current)
        if current >= len(tokens) or tokens[current]["type"] != "RPAREN":
            raise SyntaxError("Expected ')' to close yapping")
        current += 1  # skip )
        return {"type": "PrintStatement", "value": value_node}, current
    
    raise ValueError("Syntax error in block near token " + str(current))

def parse_expression(tokens, current):
    left, current = parse_primary(tokens, current)
    
    # Check for binary operators
    while current < len(tokens) and tokens[current]["type"] in ["AND", "OR", "EQ_EQ", "NE", "LT", "GT", "LE", "GE"]:
        op = tokens[current]["value"]
        current += 1
        right, current = parse_primary(tokens, current)
        left = {"type": "BinaryOp", "op": op, "left": left, "right": right}
    
    return left, current

def parse_primary(tokens, current):
    token = tokens[current]
    
    if token["type"] == "INT":
        return {"type": "Integer", "value": token["value"]}, current + 1
    
    if token["type"] == "FLOAT":
        return {"type": "Float", "value": token["value"]}, current + 1
    
    if token["type"] == "STRING":
        return {"type": "String", "value": token["value"]}, current + 1
    
    if token["type"] == "KEYWORD" and token["value"] == "noCap":
        return {"type": "Boolean", "value": True}, current + 1
    
    if token["type"] == "KEYWORD" and token["value"] == "cap":
        return {"type": "Boolean", "value": False}, current + 1
    
    if token["type"] == "IDENTIFIER":
        return {"type": "Identifier", "name": token["value"]}, current + 1
    
    raise ValueError("Unexpected token in expression: " + str(token))

def interpreter(ast):
    variables = {}
    
    def evaluate(node):
        if node["type"] == "Integer":
            return node["value"]
        if node["type"] == "Float":
            return node["value"]
        if node["type"] == "String":
            return node["value"]
        if node["type"] == "Boolean":
            return node["value"]
        if node["type"] == "Identifier":
            return variables[node["name"]]
        if node["type"] == "BinaryOp":
            left = evaluate(node["left"])
            right = evaluate(node["right"])
            op = node["op"]
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "<": return left < right
            if op == ">": return left > right
            if op == "<=": return left <= right
            if op == ">=": return left >= right
            if op == "&&": return left and right
            if op == "||": return left or right
        raise ValueError("Unknown node: " + node["type"])
    
    def execute(node):
        if node["type"] == "VariableDeclaration":
            variables[node["name"]] = evaluate(node["value"])
        
        elif node["type"] == "PrintStatement":
            print(evaluate(node["value"]))
        
        elif node["type"] == "IfStatement":
            if evaluate(node["condition"]):
                for stmt in node["body"]:
                    execute(stmt)
            else:
                ran = False
                for branch in node["elseif_branches"]:
                    if evaluate(branch["condition"]):
                        for stmt in branch["body"]:
                            execute(stmt)
                        ran = True
                        break
                if not ran and node["else_body"]:
                    for stmt in node["else_body"]:
                        execute(stmt)
    
    for stmt in ast["body"]:
        execute(stmt)

if __name__ == "__main__":
    source = readProgram()
    tokens = lexer(source)
    ast = parse(tokens)
    print("--------------AST--------------")
    print(json.dumps(ast, indent=2))
    print("\n--------------OUTPUT--------------")
    interpreter(ast)
