import requests

EARLIEST_VERSION_TO_CHECK = "v0.73.8"


def check_versions():
    vega_versions = requests.get(
        "https://api.github.com/repos/vegaprotocol/vega/releases"
    ).json()
    versions_to_check = set()
    for version in vega_versions:
        if version["tag_name"] == EARLIEST_VERSION_TO_CHECK:
            versions_to_check.add(version["tag_name"])
            break
        if version["prerelease"]:
            continue
        versions_to_check.add(version["tag_name"])

    tags = requests.get(
        "https://api.github.com/repos/vegaprotocol/vega-market-sim/tags"
    ).json()
    tagged_vega_versions = set()
    for tag in tags:
        if tag["name"].startswith("vega-"):
            tagged_vega_versions.add(tag["name"][5:])

    if versions_to_check.difference(tagged_vega_versions):
        raise Exception(f"Missing tags for vega versions: {versions_to_check}")


if __name__ == "__main__":
    check_versions()
