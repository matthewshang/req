import lxml.html
import simplejson

class Gradebook:
    def __init__(self):
        self.classes = []
        self.most_recent = []
        self.table = None
    
    def init_table(self, sems):
        num_classes = len(self.classes)
        self.table = [[Grade() for x in range(sems)] for x in range(num_classes)]

class Grade:
    def __init__(self):
        self.attribs = {}
        self.value = ''

def build_gradebook(text):
    gradebook = Gradebook()

    html = lxml.html.fromstring(text)
    classes = html.xpath('//*[contains(@id, "classDesc")]/tbody/tr/td/span/a')
    gradebook.classes = [x.text_content() for x in classes]

    start = text.find("|| {}),") + 36
    end = text.find("</script>", start) - 5
    table_text = text[start : end]

    table = simplejson.loads(table_text)
    elements = table['tb']['r']

    grades = []
    for e in elements:
        if simplejson.dumps(e).find('data-expanders') == -1:
            grades.append(e)

    num_sems = len(grades[0]['c']) - 1
    gradebook.init_table(num_sems)
    
    for i, g in enumerate(grades):
        c = g['c']
        # print(simplejson.dumps(c, indent=4 * ' '))
        last_data = -1
        for j in range(0, len(c) - 1):
            h = lxml.html.fromstring(c[j + 1]['h'])
            entry = gradebook.table[i][j]
            if len(h) > 0:
                last_data = j
                child = h[0]
                attribs = entry.attribs
                attribs['entityId'] = child.get('data-eid')
                attribs['corNumId'] = child.get('data-cni')
                attribs['track'] = child.get('data-trk')
                attribs['section'] = child.get('data-sec')
                attribs['gbId'] = child.get('data-gid')
                attribs['bucket'] = child.get('data-bkt')
                attribs['isEoc'] = child.get('data-iseoc')
            content = h.text_content()
            content = content.replace(u'\xa0', u' ').strip()
            entry.value = content
        gradebook.most_recent.append(last_data)
    
    return gradebook

if __name__ == '__main__':
    with open("gradebook.html", "r") as f:
        text = f.read()
        gradebook = build_gradebook(text)
        print(gradebook.most_recent)
        for i, row in enumerate(gradebook.table):
            print("{}: {}".format(gradebook.classes[i], [x.value for x in row]))
    