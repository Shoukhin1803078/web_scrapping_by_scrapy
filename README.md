# web_scrapping_by_scrapy

- git clone repo
- cd repo

- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

- scrapy startproject scrapytutorial
- cd scrapytutorial
- scrapy genspider example example.com
- cd scrapytutorial
- scrapy crawl example

```
web_scrapping_by_scrapy/
│
├── .gitignore
├── .env
├── requirements.txt
├── README.md
│
├── venv/                     # (ignored)
│
└── scrapytutorial/           # main scrapy project
    │
    ├── scrapy.cfg
    │
    └── scrapytutorial/
        │
        ├── __init__.py
        ├── items.py          # define data structure
        ├── pipelines.py      # process/store data
        ├── middlewares.py
        ├── settings.py
        │
        └── spiders/
            │
            ├── __init__.py
            └── example.py    # your spider
```


---

🚀 Full Command Flow (step-by-step)
1️⃣ Clone + Setup
git clone <your-repo-link>
cd web_scrapping_by_scrapy
2️⃣ Create Virtual Env
python3 -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
pip install scrapy python-dotenv
pip freeze > requirements.txt
4️⃣ Create Scrapy Project
scrapy startproject scrapytutorial
cd scrapytutorial
5️⃣ Create Spider
scrapy genspider example example.com
6️⃣ Run Spider
scrapy crawl example
7️⃣ Save Output
scrapy crawl example -o data.json
🔥 Pro Upgrade (very important)
settings.py update করো
ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
🧠 Real-world Flow (mental model)

👉 তুমি basically এই pipeline follow করতেছো:

Spider → Request → Response → Parse → Item → Pipeline → Output

