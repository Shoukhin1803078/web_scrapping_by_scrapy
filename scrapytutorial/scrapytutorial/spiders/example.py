

import logging
import os
from pathlib import Path

import scrapy
from dotenv import load_dotenv
from scrapy_playwright.page import PageMethod

# Resolve repo-root .env (works when CWD is scrapytutorial/ or elsewhere)
_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

_LOG = logging.getLogger(__name__)

# Prefer stable text over a long absolute XPath (layout changes break brittle paths).
_POST_LOGIN_HEADING = "xpath=//h2[contains(normalize-space(.), 'All opportunities on Airwork AI')]"


class ExampleSpider(scrapy.Spider):
    name = "example"

    start_urls = ["https://app.airwork.ai/login"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not EMAIL or not PASSWORD:
            _LOG.warning(
                "EMAIL or PASSWORD missing — set them in %s or the environment.",
                _env,
            )

    def start_requests(self):
        yield scrapy.Request(
            url="https://app.airwork.ai/login",
            meta={
                "playwright": True,
                "playwright_page_goto_kwargs": {"wait_until": "networkidle"},
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "input[name='email']", state="visible"),
                    PageMethod("fill", "input[name='email']", EMAIL or ""),
                    PageMethod("fill", "input[name='password']", PASSWORD or ""),
                    PageMethod("click", "button[type='submit']"),
                    PageMethod("wait_for_selector", _POST_LOGIN_HEADING, state="visible"),
                ],
            },
            callback=self.after_login,
        )

    def after_login(self, response):
        self.logger.info("AFTER LOGIN HIT")
        self.logger.info(repr(response.url))

        job_links = response.css("a::attr(href)").getall()

        for link in job_links:
            if link and "job" in link:

                full_url = (
                    "https://app.airwork.ai" + link
                    if link.startswith("/")
                    else link
                )

                yield scrapy.Request(
                    url=full_url,
                    meta={"playwright": True},
                    callback=self.parse_job,
                )

    def parse_job(self, response):

        yield {
            "title": response.css("div.flex.flex-1.flex-col.gap-0\\.5 h1::text").get(),
            "catchphrase": " ".join(response.css("div.flex.flex-1.flex-col.gap-0\\.5 p::text").getall()).strip(),
            "salary": response.xpath("//span[text()='Salary range']/following::span[1]/text()").get(),
            "job_type": response.xpath("//span[text()='Type']/following::span[1]/text()").get(),
            "job_nature": response.xpath("//span[text()='Nature']/following::span[1]/text()").get(),
            "summary": response.css("#job-summary::text").get(),
            "description": response.css("#job-description::text").get(),
        }
