""" Class to wrap around the DOM node for an IATI activity to encapsulate business logic """

import iatilocal.mappings, xpath


class IATIActivity:
    """ Read-only wrapper around a DOM node for an iati-activity to apply business logic 
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
        return {
            "ref": self.get_value("reporting-org/@ref"),
            "type": self.get_value("reporting-org/@type"),
            "type_label": self.get_label("organisation-type", "reporting-org/@type"),
            "narrative": self.get_narrative("reporting-org"),
        }

    @property
    def participating_orgs (self):
        """ Return a list of dicts representing participating orgs """
        org_list = []
        for node in self.get_nodes("participating-org"):
            org_list.append({
                "ref": self.get_value("@ref", node),
                "type": self.get_value("@type", node),
                "type_label": self.get_label("organisation-type", "@type", node),
                "role": self.get_value("@role", node),
                "role_label": self.get_label("organisation-role","@role", node),
                "narrative": self.get_narrative(".", node),
            })
        return org_list

    @property
    def iati_identifier (self):
        """ Return the IATI identifier for the activity """
        return self.get_value("iati-identifier")

    @property
    def activity_status (self):
        return {
            "code": self.get_value("activity-status/@code"),
            "label": self.get_label("activity-status", "activity-status/@code"),
        }
            

    @property
    def title (self):
        """ Return a dict of titles, keyed by ISO language code """
        return self.get_narrative("title")

    @property
    def description (self):
        """ Return a dict of descriptions, keyed by ISO language code """
        return self.get_narrative("description")

    @property
    def start_date_planned (self):
        """ Return the planned start date, or None if not defined """
        return self.get_value("activity-date[@type=1]/@iso-date")

    @property
    def start_date_actual (self):
        """ Return the actual start date, or None if not defined """
        return self.get_value("activity-date[@type=2]/@iso-date")

    @property
    def end_date_planned (self):
        """ Return the planned end date, or None if not defined """
        return self.get_value("activity-date[@type=3]/@iso-date")

    @property
    def end_date_actual (self):
        """ Return the actual end date, or None if not defined """
        return self.get_node("activity-date[@type=4]/@iso-date")

    @property
    def sectors (self):
        """ Return sectors as a map, keyed by vocabulary, then by sector code within the vocabulary """
        sector_map = {}
        for node in self.get_nodes("sector"):
            vocabulary = self.get_value("@vocabulary", base_node=node)
            sector_map.setdefault(vocabulary, {})[self.get_value("@code")] = {
                "percentage": node.getAttribute("percentage"),
                "narrative": self._narrative(node),
            }
        return sector_map

    @property
    def locations (self):
        """ Return locations as a list. """
        locations = []
        for node in self.get_nodes("location"):
            locations.append({
                "ref": self.get_value("@ref", node),
                "narrative": self.get_narrative("name", node),
                "location-class": self.get_value("location-class/@code", node),
                "location-class-label": self.get_label("location-class", "location-class/@code", node),
                "feature-designation": self.get_value("feature-designation/@code"),
            })
        return locations


    #
    # Generic XPath-based value lookup
    #

    def get_value (self, xpath_string, base_node=None):
        """ Look up a string value based on an XPath (to an element or attribute) """
        node = self.get_node(xpath_string, base_node)
        if node:
            return self._node_text(node)
        else:
            return None

    def get_label (self, type, xpath_string, base_node=None):
        """ Look up a codelist label based on an XPath (to an element or attribute) """
        code = self.get_value(xpath_string, base_node)
        if code:
            return iatilocal.mappings.get_label(type, code)
        else:
            return None

    def get_narrative(self, xpath_string, base_node=None):
        """ Look up all the available narrative elements under a node """
        node = self.get_node(xpath_string, base_node)
        if node:
            return self._narrative(node)
        else:
            return None

    def get_node (self, xpath_string, base_node=None):
        """ Look up a single DOM node by XPath """
        nodes = self.get_nodes(xpath_string, base_node)
        if len(nodes) == 0:
            return None
        else:
            return nodes[0]

    def get_nodes (self, xpath_string, base_node=None):
        """ Look up a list of DOM nodes by XPath """
        if base_node is None:
            base_node = self.activity_node
        return xpath.find(xpath_string, base_node)


    #
    # Internal utility methods
    #
        
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
        """ Extract top-level text from a DOM element or attribute node """
        if node.nodeType == node.ELEMENT_NODE:
            s = ""
            for child in node.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    s += child.nodeValue
            return s
        elif node.nodeType == node.ATTRIBUTE_NODE:
            return node.value
        else:
            raise Exception("Cannot get text for node of type {}".format(node.nodeType))
        
