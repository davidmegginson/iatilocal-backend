import xpath

class IATIActivity:
    """ Wrapper around a DOM node for an iati-activity to apply business logic 
    Focuses only on the parts of IATI useful for comparing with humanitarian 3W.

    """

    def __init__ (self, node):
        """ Create a wrapper around a DOM node for an iati-activity """
        self.node = node

    @property
    def lang (self):
        """ Return the default language for the activity report """
        return self.node.getAttribute("xml:lang")

    @property
    def reporting_org (self):
        """ Return a dict of properties describing the reporting org """
        node = xpath.find("reporting-org", self.node)[0]
        return {
            "ref": node.getAttribute("ref"),
            "type": node.getAttribute("type"),
            "narrative": self._narrative(node),
        }

    @property
    def iati_identifier (self):
        """ Return the IATI identifier for the activity """
        return self._text("iati-identifier")

    @property
    def activity_status (self):
        return xpath.find("activity-status", self.node)[0].getAttribute("code")

    @property
    def title (self):
        """ Return a dict of titles, keyed by ISO language code """
        return self._narrative(xpath.find("title", self.node)[0])

    @property
    def description (self):
        """ Return a dict of descriptions, keyed by ISO language code """
        return self._narrative(xpath.find("description", self.node)[0])

    @property
    def start_date_planned (self):
        """ Return the planned start date, or None if not defined """
        node = xpath.find("activity-date[@type=1]", self.node)
        if node:
            return node[0].getAttribute("iso-date")
        else:
            return None

    @property
    def start_date_actual (self):
        """ Return the actual start date, or None if not defined """
        node = xpath.find("activity-date[@type=2]", self.node)
        if node:
            return node[0].getAttribute("iso-date")
        else:
            return None

    @property
    def end_date_planned (self):
        """ Return the planned end date, or None if not defined """
        node = xpath.find("activity-date[@type=3]", self.node)
        if node:
            return node[0].getAttribute("iso-date")
        else:
            return None

    @property
    def end_date_actual (self):
        """ Return the actual end date, or None if not defined """
        node = xpath.find("activity-date[@type=4]", self.node)
        if node:
            return node[0].getAttribute("iso-date")
        else:
            return None

    @property
    def sectors (self):
        """ Return sectors as a map, keyed by vocabulary, then by sector code within the vocabulary """
        sector_map = {}
        nodes = xpath.find("sector", self.node)
        for node in nodes:
            vocabulary = node.getAttribute("vocabulary")
            if not vocabulary in sector_map:
                sector_map[vocabulary] = {}
            sector_map[vocabulary][node.getAttribute("code")] = {
                "percentage": node.getAttribute("percentage"),
                "narrative": self._narrative(node),
            }
        return sector_map
        
    def _text (self, expr, first=True):
        nodes = xpath.find(expr, self.node)
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
        
