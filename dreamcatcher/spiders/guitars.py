import attr
import dateparser
from scrapy import linkextractors, spiders
import textwrap


@attr.s
class Listing:
    id = attr.ib()
    name = attr.ib()
    date = attr.ib()
    price = attr.ib()
    description = attr.ib()
    url = attr.ib()

    def __str__(self):
        return self.url

class CraigslistGuitarSpider(spiders.CrawlSpider):
    name = "craigslist-guitar"
    start_urls = [
        "https://vermont.craigslist.org/search/msa?sort=date&query=guitar&postal=05641&search_distance=75"
    ]

    rules = (
        # follow next page links
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css=".button.next"),
            callback="parse_listing",
        ),
        # follow and parse postings
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css=".result-title"),
            callback="parse_listing",
        ),
    )

    def parse_listing(self, response):
        print("found listing")
        return Listing(
            id=response.url,
            name=response.css("#titletextonly::text").extract_first(),
            date=_normalize_date(
                response.css("#display-date > time").attrib["datetime"]
            ),
            price=_normalize_price(response.css(".price::text").extract_first()),
            description=CraigslistGuitarSpider._build_body(
                response.css("#postingbody::text").getall()
            ),
            url=response.url,
        )

    @staticmethod
    def _build_body(lines):
        return " ".join([line.strip() for line in lines]).strip()


def _normalize_price(price):
    try:
        return int(price.replace("$", "").replace(",", "").strip())
    except (TypeError, AttributeError):
        return None

SPIDERS = [CraigslistGuitarSpider]
