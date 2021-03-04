import collections, datetime, requests, xml.dom.pulldom
from iatilocal.iatiwrapper import IATIActivity

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
                    self.queue.append(IATIActivity(node))
            if len(self.queue) == 0:
                raise StopIteration()
            else:
                return self.__next__()

if __name__ == "__main__":
    import csv, sys

    output = csv.writer(sys.stdout)
    output.writerow([
        "Identifier",
        "Source",
        "Implementing orgs",
        "Programming orgs",
        "Funding orgs",
        "Humanitarian clusters",
        "OECD sectors",
        "Recipient countries",
        "Locations",
        "Start date planned",
        "Start date actual",
        "End date planned",
        "End date actual",
    ])
    output.writerow([
        "#activity+id",
        "#meta+source",
        "#org+impl+name+list",
        "#org+prog+name+list",
        "#org+funder+name+list",
        "#sector+cluster+list",
        "#sector+oecd+list",
        "#country+code+v_iso2",
        "#loc+name+list",
        "#date+start+planned",
        "#date+start+actual",
        "#date+end+planned",
        "#date+end+actual",
    ])
    
    activities = IATIActivityIterator(humanitarian=True, country_code="so", year_min=2019, year_max=2021)
    for activity in activities:

        output.writerow([
            activity.iati_identifier,
            "IATI",
            " | ".join([org["narrative"].get("en", "") for org in activity.participating_orgs.get("Implementing", [])]),
            " | ".join([org["narrative"].get("en", "") for org in activity.participating_orgs.get("Accountable", [])]),
            " | ".join([org["narrative"].get("en", "") for org in activity.participating_orgs.get("Funding", [])]),
            " | ".join([sector["narrative"].get("en", "") for sector in activity.sectors.get("10", {}).values()]),
            " | ".join([sector["narrative"].get("en", "") for sector in activity.sectors.get("1", {}).values()]),
            " | ".join([country["code"] for country in activity.recipient_countries]),
            " | ".join([location["narrative"].get("en", "") for location in activity.locations]),
            activity.start_date_planned,
            activity.start_date_actual,
            activity.end_date_planned,
            activity.end_date_actual,
        ])
