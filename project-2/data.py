#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB.

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to
update the street names before you save them to JSON.

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings.
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

sector_re = re.compile(r'\bSector\b', re.IGNORECASE)
dir1_re = re.compile(r'(West)', re.IGNORECASE)
dir2_re = re.compile(r'(East)', re.IGNORECASE)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

streets = {"Rd.": "Road", "St.": "Street"}

def fix_postcode(postcode):
    return postcode.replace(" ", "")

def fix_street(street):
    #street = street.lower().strip()
    if re.search(sector_re, street):
        street = street.replace("(", "")
        street = street.replace(")", "")
    if re.search(dir1_re, street):
        street = street.replace("(West)", "West")
    if re.search(dir2_re, street):
        street = street.replace("(East)", "East")
    if re.search(street_type_re, street):
        street = street.replace("St.", "Street")
        street = street.replace("Rd.", "Road")
    else:
        street = street.replace("Rd", "Road")

    return street

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way":
        tmplat, tmplon, refs = None, None, []
        node["type"] = element.tag
        # process child tags
        for l in list(element.iter()):
            if l.tag == "tag" and l.get("k", None):
                val = l.get("k")
                if re.search(problemchars, val):
                    continue
                if re.search(lower_colon, val):
                    if val.startswith("addr:"):
                        colontoks = val.split(":")
                        if len(colontoks) > 2:
                            continue
                        if not "address" in node:
                            node["address"] = {}
                        colonval = val.split(":")[1]
                        attrval = l.get("v")
                        if colonval == "street":
                            #print "got street"
                            attrval = fix_street(attrval)
                        elif colonval == "postcode":
                            attrval = fix_postcode(attrval)
                        node["address"][colonval] = attrval
                else:
                    node[val] = l.get("v")

            elif l.tag == "nd":
                refs.append(l.get("ref"))

        # Process element attributes
        for k, v in element.attrib.items():
            k = k.lower().strip()
            if k in CREATED:
                if "created" not in node:
                    node["created"] = {}
                node["created"][k] = v
            elif k in ('lat', 'lon'):
                if "pos" not in node:
                    node["pos"] = []
                if k == 'lat':
                    tmplat = float(v)
                if k == 'lon':
                    tmplon = float(v)
            else:
                node[k] = v
        # handle the latitude and longitude, if found
        if tmplat or tmplon:
            node["pos"] = [tmplat, tmplon]
            tmplat = tmplon = None
        # handle the refs, if found
        if len(refs):
            node["node_refs"] = refs
            refs = []
        #print node
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('mumbai_india.osm', True)
    #pprint.pprint(data)

    correct_first_elem = {
        "id": "261114295",
        "visible": "true",
        "type": "node",
        "pos": [41.9730791, -87.6866303],
        "created": {
            "changeset": "11129782",
            "user": "bbmiller",
            "version": "7",
            "uid": "451048",
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.",
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369",
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()
    # print fix_street("Sector 50(E)")
    # print fix_street("Sector 50D")
    # print fix_street("Sector 50 E")
    # print fix_street("MG ROad (West)")
    # print fix_street("MG Rd. (West)")
    # print fix_street("Vile Parle (East) St")