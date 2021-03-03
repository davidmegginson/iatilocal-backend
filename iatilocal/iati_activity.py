import xpath

from iatilocal.mappings import get_label

class IATIActivity:
    """ Wrapper around a DOM node for an iati-activity to apply business logic 
    Focuses only on the parts of IATI useful for comparing with humanitarian 3W.

    """

    def __init__ (self, activity_node):
        """ Create a wrapper around a DOM node for an iati-activity """
        self.activity_node = activity_node

    @property
    def lang (self):
        """ Return the default language for the activity report """
        return self.activity_node.getAttribute("xml:lang")

    @property
    def reporting_org (self):
        """ Return a dict of properties describing the reporting org """
        node = self.get_node("reporting-org")
        return {
            "ref": node.getAttribute("ref"),
            "type": node.getAttribute("type"),
            "type_label": get_label("organisation-type", node.getAttribute("type")),
            "narrative": self._narrative(node),
        }

    @property
    def participating_orgs (self):
        """ Return a list of dicts representing participating orgs """
        org_list = []
        for node in self.get_nodes("participating-org"):
            org_list.append({
                "ref": node.getAttribute("ref"),
                "type": node.getAttribute("type"),
                "type_label": get_label("organisation-type", node.getAttribute("type")),
                "role": node.getAttribute("role"),
                "role_label": get_label("organisation-role", node.getAttribute("role")),
                "narrative": self._narrative(node),
            })
        return org_list

    @property
    def iati_identifier (self):
        """ Return the IATI identifier for the activity """
        return self._text("iati-identifier")

    @property
    def activity_status (self):
        code = self.get_node("activity-status").getAttribute("code")
        return {
            "code": code,
            "label": get_label("activity-status", code),
        }
            

    @property
    def title (self):
        """ Return a dict of titles, keyed by ISO language code """
        return self._narrative(self.get_node("title"))

    @property
    def description (self):
        """ Return a dict of descriptions, keyed by ISO language code """
        return self._narrative(self.get_node("description"))

    @property
    def start_date_planned (self):
        """ Return the planned start date, or None if not defined """
        node = self.get_node("activity-date[@type=1]")
        if node:
            return node.getAttribute("iso-date")
        else:
            return None

    @property
    def start_date_actual (self):
        """ Return the actual start date, or None if not defined """
        node = self.get_node("activity-date[@type=2]")
        if node:
            return node.getAttribute("iso-date")
        else:
            return None

    @property
    def end_date_planned (self):
        """ Return the planned end date, or None if not defined """
        node = self.get_node("activity-date[@type=3]")
        if node:
            return node.getAttribute("iso-date")
        else:
            return None

    @property
    def end_date_actual (self):
        """ Return the actual end date, or None if not defined """
        node = self.get_node("activity-date[@type=4]")
        if node:
            return node.getAttribute("iso-date")
        else:
            return None

    @property
    def sectors (self):
        """ Return sectors as a map, keyed by vocabulary, then by sector code within the vocabulary """
        sector_map = {}
        for node in self.get_nodes("sector"):
            vocabulary = node.getAttribute("vocabulary")
            if not vocabulary in sector_map:
                sector_map[vocabulary] = {}
            sector_map[vocabulary][node.getAttribute("code")] = {
                "percentage": node.getAttribute("percentage"),
                "narrative": self._narrative(node),
            }
        return sector_map

    @property
    def locations (self):
        """ Return locations as a list. """
        locations = []
        for node in self.get_nodes("location"):
            pass
        return locations

    def get_node (self, xpath_string):
        nodes = self.get_nodes(xpath_string)
        if len(nodes) == 0:
            return None
        else:
            return nodes[0]

    def get_nodes (self, xpath_string):
        return xpath.find(xpath_string, self.activity_node)
        
    def _text (self, expr, first=True):
        nodes = self.get_nodes(expr)
        if not nodes:
            return None
        elif first:
            return self._node_text(nodes[0])
        else:
            return [self._node_text(node) for node in nodes]
        
    def _narrative (self, node):
        """ Return a dict of all narrative text for an element, keyed by language """
        narratives = {}
        narrative_nodes = xpath.find("narrative", node)
        for narrative_node in narrative_nodes:
            lang = narrative_node.getAttribute("xml:lang")
            if not lang:
                lang = self.lang
            narratives[lang] = self._node_text(narrative_node)
        return narratives

    def _node_text (self, node):
        """ Extract top-level text from a DOM node """
        s = ""
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                s += child.nodeValue
        return s
        
