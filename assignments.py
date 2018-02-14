import lxml.html
import simplejson

class ClassEntry:
    def __init__(self, html):
        children = [x.text_content() for x in html.iterchildren()]
       
        self.date = children[0]        
        self.name = children[1]
        self.grade = children[2]
        self.percent = children[3]
        self.points = children[4]

    def __str__(self):
        return "{}: {}, Letter {}, Percent {}, Points {}".format(
            self.date, self.name, self.grade, self.percent, self.points)

class Category:
    def __init__(self, html):
        children = [x.text_content() for x in html.iterchildren()]
        
        name_weight = children[1]
        self.name = name_weight[:name_weight.find('weight')]
        self.weight = name_weight[name_weight.find('weight'):]
        self.grade = children[2]
        self.percent = children[3]
        self.points = children[4]

        self.entries = []
    
    def add_entry(self, html):
        if len(html.getchildren()) > 1:
            self.entries.append(ClassEntry(html))

    def __str__(self):
        return "{}, Weighted {}%, Letter {}, Percent {}, Points {}".format(
            self.name, self.weight, self.grade, self.percent, self.points)

class ClassDetail:
    def __init__(self):
        self.overall_grade = ''
        self.overall_percent = ''
        self.categories = []

def build_class(text):
    class_detail = ClassDetail()

    start_key = "<output><![CDATA["
    end_key = "]]></o"
    start = text.find(start_key) + len(start_key)
    end = text.find(end_key)
    html_text = text[start : end]

    html = lxml.html.fromstring(html_text)
    tables = html.xpath('//div/table/tbody')

    summary = tables[1]
    overall_grade = summary.xpath('tr/td/span')[0]
    overall_percent = summary.xpath('tr/td[contains(@style, "!important")]')[0]
    class_detail.overall_grade = overall_grade.text_content()
    class_detail.overall_percent = overall_percent.text_content()

    details = tables[-1]
    last_cat = None
    for row in details.iterchildren():
        if 'sf_Section' in row.attrib['class']:
            category = Category(row)
            class_detail.categories.append(category)
            last_cat = category
        else:
            last_cat.add_entry(row)

    return class_detail

if __name__ == "__main__":
    with open('assignments.html', 'r') as f:
        text = f.read()
    class_detail = build_class(text)
    print("{}: {}%".format(class_detail.overall_grade, class_detail.overall_percent))
    for c in class_detail.categories:
        print(c)
        for e in c.entries:
            print("    " + str(e))