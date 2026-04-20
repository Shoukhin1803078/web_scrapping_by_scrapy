

# import logging
# import os
# from pathlib import Path

# import scrapy
# from dotenv import load_dotenv
# from scrapy_playwright.page import PageMethod

# # Resolve repo-root .env (works when CWD is scrapytutorial/ or elsewhere)
# _env = Path(__file__).resolve().parents[3] / ".env"
# load_dotenv(_env)

# EMAIL = os.getenv("EMAIL")
# PASSWORD = os.getenv("PASSWORD")

# _LOG = logging.getLogger(__name__)

# # Prefer stable text over a long absolute XPath (layout changes break brittle paths).
# _POST_LOGIN_HEADING = "xpath=//h2[contains(normalize-space(.), 'All opportunities on Airwork AI')]"


# class ExampleSpider(scrapy.Spider):
#     name = "example"

#     start_urls = ["https://app.airwork.ai/login"]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not EMAIL or not PASSWORD:
#             _LOG.warning(
#                 "EMAIL or PASSWORD missing — set them in %s or the environment.",
#                 _env,
#             )

#     def start_requests(self):
#         yield scrapy.Request(
#             url="https://app.airwork.ai/login",
#             meta={
#                 "playwright": True,
#                 "playwright_page_goto_kwargs": {"wait_until": "networkidle"},
#                 "playwright_page_methods": [
#                     PageMethod("wait_for_selector", "input[name='email']", state="visible"),
#                     PageMethod("fill", "input[name='email']", EMAIL or ""),
#                     PageMethod("fill", "input[name='password']", PASSWORD or ""),
#                     PageMethod("click", "button[type='submit']"),
#                     PageMethod("wait_for_selector", _POST_LOGIN_HEADING, state="visible"),
#                 ],
#             },
#             callback=self.after_login,
#         )

#     def after_login(self, response):
#         self.logger.info("AFTER LOGIN HIT")
#         self.logger.info(repr(response.url))

#         job_links = response.css("a::attr(href)").getall()

#         for link in job_links:
#             if link and "job" in link:

#                 full_url = (
#                     "https://app.airwork.ai" + link
#                     if link.startswith("/")
#                     else link
#                 )

#                 yield scrapy.Request(
#                     url=full_url,
#                     meta={"playwright": True},
#                     callback=self.parse_job,
#                 )

#     def parse_job(self, response):

#         yield {
#             "title": response.css("div.flex.flex-1.flex-col.gap-0\\.5 h1::text").get(),
#             "catchphrase": " ".join(response.css("div.flex.flex-1.flex-col.gap-0\\.5 p::text").getall()).strip(),
#             "salary": response.xpath("//span[text()='Salary range']/following::span[1]/text()").get(),
#             "job_type": response.xpath("//span[text()='Type']/following::span[1]/text()").get(),
#             "job_nature": response.xpath("//span[text()='Nature']/following::span[1]/text()").get(),
#             "summary": response.css("#job-summary::text").get(),
#             "description": response.css("#job-description::text").get(),
#         }



# import scrapy
# import os
# from dotenv import load_dotenv

# load_dotenv()

# EMAIL = os.getenv("EMAIL")
# PASSWORD = os.getenv("PASSWORD")


# class AirworkSpider(scrapy.Spider):
#     name = "airwork"

#     def start_requests(self):
#         yield scrapy.Request(
#             url="https://app.airwork.ai/login",
#             meta={
#                 "playwright": True,
#                 "playwright_include_page": True,
#             },
#             callback=self.parse_login,
#         )

#     # -------------------------
#     # 1. LOGIN
#     # -------------------------
#     async def parse_login(self, response):
#         page = response.meta["playwright_page"]

#         await page.fill("input[name='email']", EMAIL)
#         await page.fill("input[name='password']", PASSWORD)
#         await page.click("button[type='submit']")

#         # ✅ wait until dashboard loads
#         await page.wait_for_selector(
#             "h2:has-text('All opportunities on Airwork AI')",
#             timeout=15000
#         )

#         print("Login Successful ✅")

#         # 🔥 IMPORTANT: go to jobs page instead of closing page
#         await page.goto("https://app.airwork.ai/jobs")

#         # pass same page to next callback
#         yield scrapy.Request(
#             url="https://app.airwork.ai/jobs",
#             meta={
#                 "playwright": True,
#                 "playwright_page": page,   # 🔥 reuse logged-in session
#                 "playwright_include_page": True,
#             },
#             callback=self.parse_jobs_list,
#         )

#     # -------------------------
#     # 2. JOB LIST PAGE
#     # -------------------------
#     async def parse_jobs_list(self, response):
#         page = response.meta["playwright_page"]

#         await page.wait_for_selector("div.flex.flex-col.gap-8")

#         job_links = await page.eval_on_selector_all(
#             "div.flex.flex-col.gap-8 a[target='_blank']",
#             "els => els.map(e => e.getAttribute('href'))"
#         )

#         for link in job_links:
#             yield scrapy.Request(
#                 response.urljoin(link),
#                 meta={
#                     "playwright": True,
#                     "playwright_page": page,
#                     "playwright_include_page": True,
#                 },
#                 callback=self.parse_job_detail,
#             )

#         # -------------------------
#         # PAGINATION
#         # -------------------------
#         next_btn = await page.query_selector("a[aria-label='Go to next page']")

#         if next_btn:
#             await next_btn.click()
#             await page.wait_for_timeout(2000)

#             yield scrapy.Request(
#                 page.url,
#                 meta={
#                     "playwright": True,
#                     "playwright_page": page,
#                     "playwright_include_page": True,
#                 },
#                 callback=self.parse_jobs_list,
#             )
#         else:
#             await page.close()

#     # -------------------------
#     # 3. JOB DETAIL PAGE
#     # -------------------------
#     async def parse_job_detail(self, response):
#         page = response.meta["playwright_page"]

#         await page.wait_for_selector("header")

#         headline = await page.eval_on_selector("header h1", "el => el?.innerText")
#         catchphrase = await page.eval_on_selector("header p", "el => el?.innerText")

#         yield {
#             "job_url": response.url,
#             "headline": headline,
#             "catchphrase": catchphrase,
#         }



import scrapy
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


class AirworkSpider(scrapy.Spider):
    name = "airwork"

    def start_requests(self):
        yield scrapy.Request(
            "https://app.airwork.ai/login",
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },
            callback=self.parse_login,
        )

    async def parse_login(self, response):
        page = response.meta["playwright_page"]

        # LOGIN
        await page.fill("input[name='email']", EMAIL)
        await page.fill("input[name='password']", PASSWORD)
        await page.click("button[type='submit']")

        # WAIT DASHBOARD (talent page)
        await page.wait_for_selector(
            "h2:has-text('All opportunities on Airwork AI')",
            timeout=15000
        )

        print("Login Successful ✅")

        # # 🔥 YOU ARE NOW IN TALENT PAGE (IMPORTANT FIX)
        # await page.wait_for_selector("div.flex.flex-col.gap-8")

        # # -------------------------
        # # JOB LINKS FROM TALENT PAGE
        # # -------------------------
        # job_links = await page.eval_on_selector_all(
        #     "div.flex.flex-col.gap-8 a[target='_blank']",
        #     "els => els.map(e => e.getAttribute('href'))"
        # )

        # results = []

        # for link in job_links:
        #     full_url = "https://app.airwork.ai" + link

        #     await page.goto(full_url)
        #     await page.wait_for_selector("header")

        #     headline = await page.eval_on_selector("header h1", "el => el?.innerText")
        #     catchphrase = await page.eval_on_selector("header p", "el => el?.innerText")

        #     results.append({
        #         "job_url": full_url,
        #         "headline": headline,
        #         "catchphrase": catchphrase
        #     })

        #     # go back to talent page
        #     await page.go_back()
        #     await page.wait_for_selector("div.flex.flex-col.gap-8")

        # await page.close()

        yield {
            "Hello": "successfully logged in"
        }