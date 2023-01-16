"""Replace the nodes from linkcode with nodes that use a "linkcode-link" class (for CSS styling) and customizable text"""

from typing import Any, Dict

from docutils import nodes
from docutils.nodes import Node

import sphinx
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _


def doctree_read(app: Sphinx, doctree: Node) -> None:
    env = app.builder.env

    link_text = getattr(env.config, 'linkcode_link_text')
    linkcode_url = getattr(env.config, 'linkcode_url')

    for objnode in list(doctree.findall(addnodes.desc)):
        if objnode.get('domain') != 'py':
            continue

        for signode in objnode:
            if not isinstance(signode, addnodes.desc_signature):
                continue

            for child in signode.children:
                if not isinstance(child, addnodes.only):
                    continue

                onlynode = child
                for only_child in onlynode.children:
                    if not isinstance(only_child, nodes.reference):
                        continue

                    ref_node = only_child
                    refuri = ref_node.get("refuri", None)
                    if not refuri.startswith(linkcode_url.split('{')[0]):
                        continue

                    new_inline = nodes.inline('', _(f'{link_text}'), classes=['linkcode-link'])
                    new_onlynode = addnodes.only(expr='html')
                    new_onlynode += nodes.reference('', '', new_inline, internal=False, refuri=refuri)

                    onlynode.replace_self(new_onlynode)


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect('doctree-read', doctree_read)
    app.add_config_value('linkcode_link_text', '[source]', '')
    app.add_config_value('linkcode_url', None, '')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
