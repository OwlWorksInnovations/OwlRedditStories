from reddit import scrape_reddit

def get_posts(count: int):
    scrape_reddit(count)

if __name__ == "__main__":
    get_posts(1)
