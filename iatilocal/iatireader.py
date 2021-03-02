import collections, datetime, requests, xml.dom.pulldom
from iatilocal.iati_activity import IATIActivity

API_ENDPOINT = "http://www.d-portal.org/q"

class IATIActivityIterator:
    """ Iterator over IATI activities from D-Portal """

    def __init__ (self, country_code=None, humanitarian=False, year_min=None, year_max=None, status_code=None, limit=25):
        self.params = {
            "select": "*",
            "from": "act,country,sector",
            "form": "xml",
            "country_code": country_code,
            "*@humanitarian": (1 if humanitarian else None),
            "status_code": status_code,
            "limit": limit,
            "offset": 0,
        }

        # weird epoch stuff
        if year_min is not None:
            self.params["day_end_lteq"] = (datetime.datetime(year_min, 12, 31) - datetime.datetime(1970, 1, 1)).days
        if year_max is not None:
            self.params["day_start_gteq"] = (datetime.datetime(year_min, 1, 1) - datetime.datetime(1970, 1, 1)).days

        self.queue = collections.deque()

    def __iter__ (self):
        return self

    def __next__ (self):
        if len(self.queue) > 0:
            return self.queue.popleft()
        else:
            result = requests.get(API_ENDPOINT, params=self.params)
            self.params["offset"] += self.params["limit"]
            dom = xml.dom.pulldom.parseString(result.text)
            for event, node in dom:
                if event == xml.dom.pulldom.START_ELEMENT and node.tagName == 'iati-activity':
                    dom.expandNode(node)
                    self.queue.append(node)
            if len(self.queue) == 0:
                raise StopIteration()
            else:
                return self.__next__()

if __name__ == "__main__":
    import json
    activity_nodes = IATIActivityIterator(humanitarian=True, country_code="so", year_min=2021, year_max=2021)

    json_out = []
    
    for activity_node in activity_nodes:
        activity = IATIActivity(activity_node)
        json_out.append({
            "reporting-org": activity.reporting_org,
            "iati-identifier": activity.iati_identifier,
            "title": activity.title.get("en"),
            "description": activity.description.get("en"),
            "sectors": activity.sectors,
            "start_date_planned": activity.start_date_planned,
            "start_date_actual": activity.start_date_actual,
            "end_date_planned": activity.end_date_planned,
            "end_date_actual": activity.end_date_actual,
            "activity_status": activity.activity_status,
        })

    print(json.dumps(json_out, indent=2))
