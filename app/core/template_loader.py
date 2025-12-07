import os

def load_template(filename: str) -> str:
    """
    Loads a template text file from the /templates folder.

    Usage:
        load_template("query_gen_prompt.txt")
    """
    # Determine absolute path to the templates directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")

    full_path = os.path.join(templates_dir, filename)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Template file not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
