from reddit import scrape_reddit
from format import format_posts

def get_posts(count: int):
    scrape_reddit(count)

if __name__ == "__main__":
    get_posts(1)
    format_posts()
