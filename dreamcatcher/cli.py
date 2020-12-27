import click
import dateparser
import multiprocessing
import os
from pydispatch import dispatcher
from scrapy import crawler, signals, signalmanager
from scrapy.utils import project
import time
import textwrap

from . import spiders
from . import notification


@click.group()
def cli():
    pass


@cli.command()
@click.argument("category")
@click.option("--within", default="2 hours")
@click.option("--bell", default="no")
def crawl(category, within, bell):
    spiders = get_spiders(category)
    results = run_spiders(spiders[:-1])
    filtered_results = filter_results(results, within)
    click.echo(
        f"Found {len(results)} total results, {len(filtered_results)} within the last {within}"
    )
    print_results(filtered_results, bell)


@cli.command()
@click.argument("category")
@click.option("--bell", default="no")
@click.option("--interval", default="60")
def catch(category, bell, interval):
    spiders = get_spiders(category)
    last_ids = get_ids(run_spiders(spiders))

    click.echo(f"Tracking {len(last_ids)} total results, monitoring for new ones...")

    while True:
        time.sleep(int(interval))

        results = run_spiders(spiders)

        new_results = [result for result in results if result.id not in last_ids]

        click.echo(
            f"Found {len(results)} total results, {len(new_results)} new result(s)"
        )

        if new_results:
            if bell == "yes":
                ring_bell()
            notification.send_notification(new_results, category)
            print_results(new_results, bell)

        [last_ids.add(result.id) for result in results]


def get_ids(results):
    return set(result.id for result in results)


@click.pass_context
def get_spiders(ctx, category):
    if category == "apartments":
        return spiders.apartments.SPIDERS
    elif category == "guitars":
        return spiders.guitars.SPIDERS
    else:
        raise click.BadArgumentUsage(f"unknown category '{category}'", ctx)


def run_spiders(_spiders):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_run_spider_impl,
        args=(
            _spiders,
            queue,
        ),
    )
    process.start()
    results = queue.get()
    process.join()

    return results


def _run_spider_impl(_spiders, queue):
    results = []

    def _results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(_results, signal=signals.item_passed)

    process = crawler.CrawlerProcess(project.get_project_settings())
    [process.crawl(spider) for spider in _spiders]
    click.echo(
        f"Starting {len(_spiders)} spiders: {', '.join([spider.name for spider in _spiders])}..."
    )
    process.start()

    queue.put(results)


def filter_results(results, within):
    min_created_at = dateparser.parse(
        f"{within} ago",
        settings={"TIMEZONE": "US/Eastern", "RETURN_AS_TIMEZONE_AWARE": True},
    )
    return [result for result in results if result.date > min_created_at]


def print_results(results, bell):
    if results:
        results = sorted(results, key=lambda result: result.date, reverse=True)
        click.echo("Results:")
        [click.echo(textwrap.indent(str(result), "  ")) for result in results]
        if bell == "yes":
            ring_bell()


def ring_bell():
    for i in range(5):
        os.system("tput bel")
        time.sleep(1)
