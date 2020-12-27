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


class ApartmentsComSpider(spiders.CrawlSpider):
    name = "apartments_com"
    start_urls = [
        "https://www.apartments.com/under-2500/?sk=1a4c3d58ecbdfd757ab712ef4b12831f&bb=y0ho04yj7H176m3ie&so=8"
    ]

    rules = (
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css=".placardTitle"),
            callback="parse_listing",
        ),
    )

    def parse_listing(self, response):
        return Listing(
            id=response.url,
            name=response.css(".propertyName::text").extract_first().strip(),
            date=_normalize_date(
                response.css(".lastUpdated span::text").extract_first()
            ),
            price=_normalize_price(response.css(".rentAmount::text").extract_first()),
            description=response.css("#descriptionSection > p::text").getall(),
            url=response.url,
        )


class CraigslistSpider(spiders.CrawlSpider):
    name = "craigslist"
    start_urls = [
        "https://vermont.craigslist.org/search/apa?sort=date&bundleDuplicates=1&search_distance=27&postal=05602&availabilityMode=0&sale_date=all+dates"
        #"https://vermont.craigslist.org/search/msa?sort=date&query=guitar&postal=05641&search_distance=75"
    ]

    rules = (
        # follow next page links
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css=".button.next"),
        ),
        # follow and parse postings
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css=".result-title"),
            callback="parse_listing",
        ),
    )

    def parse_listing(self, response):
        return Listing(
            id=response.url,
            name=response.css("#titletextonly::text").extract_first(),
            date=_normalize_date(
                response.css("#display-date > time").attrib["datetime"]
            ),
            price=_normalize_price(response.css(".price::text").extract_first()),
            description=CraigslistSpider._build_body(
                response.css("#postingbody::text").getall()
            ),
            url=response.url,
        )

    @staticmethod
    def _build_body(lines):
        return " ".join([line.strip() for line in lines]).strip()


class RentComSpider(spiders.CrawlSpider):
    name = "rent_com"
    start_urls = [
        "https://www.rent.com/vermont/montpelier/apartments_condos_houses_townhouses?boundingbox=-73.076,43.94,-72.094,44.507"
    ]

    user_agent = "PostmanRuntime/7.26.3"

    rules = (
        # follow next page links
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css='a[data-tid="pagination-next"]'),
        ),
        # follow and parse postings
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css='a[data-tid="property-title"]'),
            follow=False,
            callback="parse_listing",
        ),
    )

    def parse_listing(self, response):
        return Listing(
            id=response.url,
            name="",
            # name=response.css(
            #     '[data-testid="home-details-summary-headline"]::text'
            # ).extract_first(),
            date=_normalize_date("now"),
            price=None,
            description="",
            url=response.url,
        )

    @staticmethod
    def _build_body(lines):
        return " ".join([line.strip() for line in lines]).strip()


def _normalize_date(date):
    return dateparser.parse(
        date, settings={"TIMEZONE": "US/Eastern", "RETURN_AS_TIMEZONE_AWARE": True}
    )


def _normalize_price(price):
    try:
        return int(price.replace("$", "").replace(",", "").strip())
    except (TypeError, AttributeError):
        return None


class StoneBrowningSpider(spiders.CrawlSpider):
    name = "stone_browning"
    start_urls = ["https://stonebrown.appfolio.com/listings/listings"]

    rules = (
        # follow and parse postings
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css=".js-listing-title a"),
            callback="parse_listing",
        ),
    )

    def parse_listing(self, response):
        return Listing(
            id=response.url,
            name="",
            # name=response.css(
            #     '[data-testid="home-details-summary-headline"]::text'
            # ).extract_first(),
            date=_normalize_date("now"),
            price=None,
            description="",
            url=response.url,
        )

    @staticmethod
    def _build_body(lines):
        return " ".join([line.strip() for line in lines]).strip()


class GarrettsPropertiesSpider(spiders.CrawlSpider):
    name = "garretts_properties"
    start_urls = ["https://www.garrettsproperties.com/rent/availableunits"]

    rules = (
        # follow and parse postings
        spiders.Rule(
            linkextractors.LinkExtractor(restrict_css="a.residential-listing"),
            callback="parse_listing",
        ),
    )

    def parse_listing(self, response):
        return Listing(
            id=response.url,
            name="",
            # name=response.css(
            #     '[data-testid="home-details-summary-headline"]::text'
            # ).extract_first(),
            date=_normalize_date("now"),
            price=None,
            description="",
            url=response.url,
        )


#SPIDERS = [ApartmentsComSpider, CraigslistSpider, RentComSpider, StoneBrowningSpider, GarrettsPropertiesSpider]
SPIDERS = [CraigslistSpider]
