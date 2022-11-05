import requests
import json
import time
from datetime import datetime


class NoAdvertSummaryError(Exception):
    pass


class RequestNotSuccessfullError(Exception):
    pass


def get_data_from_willhaben(
    page: int = 1, price_to: int = 0, price_from: int = 0
) -> str:
    """
    Scrap Willhaben Gebrauchtwagenboerse and return full html as string.
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
        params["page"] = page

    if price_to > 0 and type(price_to) == int:
        params["PRICE_TO"] = price_to

    if price_from > 0 and type(price_from) == int:
        params["PRICE_FROM"] = price_from

    r = requests.get(url, cookies=cookies, params=params, timeout=60)

    if not r.ok:
        raise RequestNotSuccessfullError("Request was not successful", url)

    return r.text


def extract_json(html: str):
    """
    Extract JSON with id=NEXT_DATA
    """
    if "__NEXT_DATA__" and "advertSummaryList" not in html:
        raise ValueError("No script tag with id='__NEXT_Data__'")

    script_tag_open = """<script id="__NEXT_DATA__" type="application/json">"""
    script_tag_close = """</script>"""
    start = html.find(script_tag_open) + len(script_tag_open)
    end = start + html[start:].find(script_tag_close)

    JSON = json.loads(html[start:end])
    data = JSON["props"]["pageProps"]["searchResult"]["advertSummaryList"]

    if len(data["advertSummary"]) == 0:
        raise NoAdvertSummaryError("Empty advertSummary")

    return data


if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d")
    try:
        # Scrap all until price < 25000
        for page in range(1000):
            time.sleep(0.5)
            for i in range(5):
                try:
                    html = get_data_from_willhaben(page, price_to=24_999)
                    data = extract_json(html)

                    with open(
                        f"./data/{now}_page={page}-price_to_24999.json",
                        "w",
                        encoding="utf-8",
                    ) as file:
                        json.dump(data, file, indent=2, ensure_ascii=False)
                        print(f"Page: {page}, price_to: 24999, saved to {file.name}")
                    break

                except RequestNotSuccessfullError as e:
                    print(e)
                    time.sleep(i * 10)

                except NoAdvertSummaryError:
                    break

        # Scrap all from price > 25000
        for page in range(1000):
            time.sleep(0.5)
            for i in range(5):
                try:
                    html = get_data_from_willhaben(page, price_from=25_000)
                    data = extract_json(html)

                    with open(
                        f"./data/{now}_page={page}-price_from_25000.json",
                        "w",
                        encoding="utf-8",
                    ) as file:
                        json.dump(data, file, indent=2, ensure_ascii=False)
                        print(f"Page: {page}, price_from: 24999, saved to {file.name}")
                    break

                except RequestNotSuccessfullError as e:
                    print(e)
                    time.sleep(i * 10)

                except NoAdvertSummaryError:
                    break

    except KeyboardInterrupt:
        print("Code stopped with CTRL+C")
