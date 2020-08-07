from urllib.parse import urljoin
import bs4

class MarkdownConverter(object):
    def __init__(self, href=None, rules=None):
        self.href = href or ''
        self.rules = rules or dict()

    def process_node(self, node):
        text = ''
        for tag in node.children:
            if isinstance(tag, bs4.NavigableString):
                text += tag.strip('\n').replace('\n', ' ')
            else:
                convert = getattr(self, f'convert_{tag.name}', None)
                if convert:
                    text += convert(tag, self.process_node(tag))
                elif tag.name in self.rules:
                    text += self.rules[tag.name](tag, self.process_node(tag))
        return text.replace('\n\n\n', '\n\n')

    def convert_a(self, node, text):
        href = node.get('href', None)
        if href:
            href = urljoin(self.href, href)
            if href == text:
                text = f'<{href}>'
            else:
                text = f'[{text}]({href})'
        return text

    def convert_p(self, node, text):
        return f'{text}\n\n'

    def convert_br(self, node, text):
        return f'  \n'

    def convert_h1(self, node, text):
        return f'# {text}\n\n'

    def convert_em(self, node, text):
        return f'*{text}*'

    def convert_strong(self, node, text):
        return f'**{text}**'

    def convert_ul(self, node, text):
        return f'\n{text}\n'
    
    def convert_ol(self, node, text):
        return f'\n{text}\n'

    def convert_li(self, node, text):
        parent = node.parent
        if getattr(parent, 'name', None) == 'ol':
            index = parent.findChildren('li').index(node) + 1
            bullet = f'{index}.'
        else:
            bullet = '*'
        indent = ''
        while parent:
            if parent.name == 'li':
                indent += '  '
            parent = parent.parent
        return f'{indent}{bullet} {text}\n'

def read(fragment, **kwargs):
    soup = bs4.BeautifulSoup(f'<div id="markdown">{fragment}</div>', features='lxml')
    root = soup.find(id='markdown')
    return MarkdownConverter(**kwargs).process_node(root)
