# -*- encoding: utf-8


def pprint_nested_tree(tree, indent=0):
    lines = []

    if indent == 0:
        lines.append(".")

    if isinstance(tree, str):
        return tree

    # This is a bit of a hard-coded fudge for a common case that causes it
    # to be printed in a slightly more useful way.
    if tree.keys() == {"latest", "prod", "stage"}:
        entries = [
            ("latest", tree["latest"]),
            ("stage", tree["stage"]),
            ("prod", tree["prod"])
        ]
    else:
        entries = sorted(tree.items())

    for i, (key, nested_tree) in enumerate(entries, start=1):
        if i == len(entries):
            lines.append("└── " + key)

            if isinstance(nested_tree, str):
                lines[-1] = lines[-1].ljust(40) + nested_tree
            else:
                lines.extend([
                    "    " + l
                    for l in pprint_nested_tree(nested_tree, indent=indent + 1)
                ])
        else:
            lines.append("├── " + key)
            if isinstance(nested_tree, str):
                lines[-1] = lines[-1].ljust(40) + nested_tree
            else:
                lines.extend([
                    "│   " + l
                    for l in pprint_nested_tree(nested_tree, indent=indent + 1)
                ])

    return lines


def build_tree_from_paths(paths):
    tree = {}

    for path, value in paths.items():
        curr_tree = tree
        path_components = path.strip("/").split("/")
        for component in path_components:
            try:
                curr_tree = curr_tree[component]
            except KeyError:
                if component == path_components[-1]:
                    curr_tree[component] = value
                else:
                    curr_tree[component] = {}
                curr_tree = curr_tree[component]

    return tree


def pprint_path_keyval_dict(paths):
    tree = build_tree_from_paths(paths)
    return pprint_nested_tree(tree)
