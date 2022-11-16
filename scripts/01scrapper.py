import requests
import json
import time
from datetime import datetime
from typing import Dict


class JSONDataError(Exception):
    pass


class RequestNotSuccessfulError(Exception):
    pass


def get_html_from_willhaben(page: int = 1, price_to: int = 0, price_from: int = 0) -> str:
    """
    Scrap Willhaben Gebrauchtwagenboerse and return page html as string 
    """
    url = "https://www.willhaben.at/iad/gebrauchtwagen/auto/gebrauchtwagenboerse"
    cookies = {
        "IADVISITOR": "a58cf0e4-74a9-40c3-bf44-5fb0b9a714bc",
        "context": "prod",
        "TRACKINGID": "75349b84-607f-4161-9bc4-99f8aeddb123",
        "x-bbx-csrf-token": "5a4f4a0d-f121-4146-9f59-32ebcac0663d",
        "SRV": "1|Y0bcV",
        "didomi_token": "eyJ1c2VyX2lkIjoiMTgzY2NjY2EtYTMzZS02ZTA4LTkxOGYtMDNkOWYxYTIzM2U1IiwiY3JlYXRlZCI6IjIwMjItMTAtMTJUMTU6MjU6MTEuMjEyWiIsInVwZGF0ZWQiOiIyMDIyLTEwLTEyVDE1OjI1OjExLjIxMloiLCJ2ZW5kb3JzIjp7ImVuYWJsZWQiOlsiYW1hem9uIiwiZ29vZ2xlIiwiYzpvZXdhLVhBUW1HU2duIiwiYzphbWF6b24tbW9iaWxlLWFkcyIsImM6aG90amFyIiwiYzp1c2Vyem9vbSIsImM6YW1hem9uLWFzc29jaWF0ZXMiLCJjOnh4eGx1dHprLW05ZlFrUHRMIiwiYzpvcHRpb25hbGUtYm5BRXlaeHkiXX0sInB1cnBvc2VzIjp7ImVuYWJsZWQiOlsieHh4bHV0enItcWtyYXAzM1EiLCJnZW9sb2NhdGlvbl9kYXRhIiwiZGV2aWNlX2NoYXJhY3RlcmlzdGljcyJdfSwidmVuZG9yc19saSI6eyJlbmFibGVkIjpbImdvb2dsZSIsImM6d2lsbGhhYmVuLVpxR242WXh6Il19LCJ2ZXJzaW9uIjoyLCJhYyI6IkFrdUFFQUZrQkpZQS5Ba3VBQ0FrcyJ9",
        "RANDOM_USER_GROUP_COOKIE_NAME": "48",
        "euconsent-v2": "CPgvCMAPgvCMAAHABBENCkCsAP_AAH_AAAAAG9tf_X_fb2_j-_59f_t0eY1P9_7_v-0zjhedk-8Nyd_X_L8X52M7vB36pq4KuR4ku3LBAQdlHOHcTQmw6IkVqSPsbk2Mr7NKJ7PEmlMbOydYGH9_n1XT-ZKY79__f_7z_v-v___37r__7-3f3_vp9V-BugBJhq3EAXYljgTbRhFAiBGFYSHQCgAooBhaIDCAlcFOyuAn1hAgAQCgCMCIEOAKMGAQAAAQBIREAIEeCAAAEQCAAEACoRCAAjQBBQASBgEAAoBoWAEUAQgSEGRARFKYEBEiQUE8gQglB_oYYQh1FAAA.f_gAD_gAAAAA",
        "_pbjs_userid_consent_data": "3265244935257896",
        "COUNTER_FOR_ADVERTISING_FIRST_PARTY_UID_V2": "0",
    }
    params = {"rows": 75}

    if page > 0 and type(page) == int:
        params.update({"page": page})

    if price_to > 0 and type(price_to) == int:
        params.update({"PRICE_TO": price_to})

    if price_from > 0 and type(price_from) == int:
        params.update({"PRICE_FROM": price_from})

    r = requests.get(url, cookies=cookies, params=params, timeout=60)

    if not r.ok:
        raise RequestNotSuccessfulError("Request was not successful", page)

    return r.text


def extract_json_from_html(html: str) -> Dict:
    """
    Extract JSON from Next.js page (Willhaben), by searching for id=NEXT_DATA
    """
    if "__NEXT_DATA__" not in html:
        raise JSONDataError("No script tag with id='__NEXT_Data__'")

    if "advertSummaryList" not in html:
        raise JSONDataError("No advertSummaryList in JSON Data")    

    script_tag_open = """<script id="__NEXT_DATA__" type="application/json">"""
    script_tag_close = """</script>"""
    start = html.find(script_tag_open) + len(script_tag_open)
    end = start + html[start:].find(script_tag_close)

    json_data = json.loads(html[start:end])
    data = json_data["props"]["pageProps"]["searchResult"]["advertSummaryList"]

    if len(data["advertSummary"]) == 0:
        raise JSONDataError("Empty advertSummary")

    return data


def loop_scrap_save(pages: int = 999, price_to: int = 0, price_from: int = 0):
    """
    Set Price Filter, loop through all pages and save scrapped json
    """
    now = datetime.now().strftime("%Y-%m-%d")

    for page in range(1, pages+1):
        time.sleep(0.5)
        for retry in range(5):
            try:
                html = get_html_from_willhaben(page, price_to, price_from)
                data = extract_json_from_html(html)

                if price_from > 0:
                    file_name = f"./json/{now}_page={page}-price_from_{price_from}.json"

                if price_to > 0: 
                    file_name = f"./json/{now}_page={page}-price_to_{price_to}.json"

                with open(file_name, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                    print(f"Page: {page}, saved to {file_name}")
                
                break  # break retry loop

            except RequestNotSuccessfulError as e:
                print(e)
                time.sleep(10 + 10*retry)

            except JSONDataError as e:
                print(e)
                break

if __name__ == "__main__":
    try:
        loop_scrap_save(price_to=24999)        
        loop_scrap_save(price_from=25000)

    except KeyboardInterrupt:
        print("Code stopped with CTRL+C")
