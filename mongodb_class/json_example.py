# To experiment with this code freely you will have to run this code locally.
# We have provided an example json output here for you to look at,
# but you will not be able to run any queries through our UI.
import json
import requests


BASE_URL = "http://musicbrainz.org/ws/2/"
ARTIST_URL = BASE_URL + "artist/"

query_type = {  "simple": {},
                "atr": {"inc": "aliases+tags+ratings"},
                "aliases": {"inc": "aliases"},
                "releases": {"inc": "releases"}}


def query_site(url, params, uid="", fmt="json"):
    params["fmt"] = fmt
    r = requests.get(url + uid, params=params)
    print "requesting", r.url

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def query_by_name(url, params, name):
    params["query"] = "artist:" + name
    return query_site(url, params)


def pretty_print(data, indent=4):
    if type(data) == dict:
        print json.dumps(data, indent=indent, sort_keys=True)
    else:
        print data


def bands_named_first_aid_kit():
    results = query_by_name(ARTIST_URL, query_type["simple"], "First Aid Kit")
    artists = results.get("artists")
    num = 0
    for r in artists:
        if r.get("name").upper().strip() == "FIRST AID KIT":
            num += 1
    print num

def queen_begin_area():
    results = query_by_name(ARTIST_URL, query_type["simple"], "QUEEN")
    artists = results.get("artists")
    for r in artists:
        if r.get("name").upper().strip() == "QUEEN":
            print r.get('begin-area'),  r

def beatles_spanish_alias():
    results = query_by_name(ARTIST_URL, query_type["simple"], "THE BEATLES")
    artists = results.get("artists")
    for r in artists:
        if r.get("name").upper().strip() == "THE BEATLES":
            aliases = r.get('aliases')
            for alias in aliases:
                if alias.get('locale') == 'es':
                    print alias.get('name')

def nirvana_disambig():
    results = query_by_name(ARTIST_URL, query_type["simple"], "NIRVANA")
    artists = results.get("artists")
    for r in artists:
        if r.get("name").upper().strip() == "NIRVANA":
            print r.get("disambiguation")

def one_direction_formed():
    results = query_by_name(ARTIST_URL, query_type["simple"], "one direction")
    artists = results.get("artists")
    for r in artists:
        if r.get("name").upper().strip() == "ONE DIRECTION":
            print r.get("disambiguation")


def main():
    #bands_named_first_aid_kit()
    queen_begin_area()
    #beatles_spanish_alias()
    #nirvana_disambig()
    one_direction_formed()
    if True:
        return
    results = query_by_name(ARTIST_URL, query_type["simple"], "First Aid Kit")
    pretty_print(results)

    artist_id = results["artists"][1]["id"]
    print "\nARTIST:"
    pretty_print(results["artists"][1])

    artist_data = query_site(ARTIST_URL, query_type["releases"], artist_id)
    releases = artist_data["releases"]
    print "\nONE RELEASE:"
    pretty_print(releases[0], indent=2)
    release_titles = [r["title"] for r in releases]

    print "\nALL TITLES:"
    for t in release_titles:
        print t


if __name__ == '__main__':
    main()
