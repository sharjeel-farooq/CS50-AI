import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = dict()
    links = corpus.get(page, set())
    num_links = len(links)
    total_pages = len(corpus)

    for p in corpus:
        distribution[p] = (1 - damping_factor) / total_pages
        if p in links:
            distribution[p] += damping_factor / num_links

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and va lues are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    
    page = random.choice(list(corpus.keys()))
    visit_counts = {page: 0 for page in corpus}
    
    for _ in range(n):
        visit_counts[page] += 1
        trans_prob = transition_model(corpus, page, damping_factor)
        page = random.choices(
            population = list(trans_prob.keys()),
            weights = list(trans_prob.values())
        )[0]
        
    page_rank = {page: count/n for page, count in visit_counts.items()}
    return page_rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.


    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    num_pages = len(corpus)
    
    page_rank = {page: 1 / num_pages for page in corpus}
    
    while True:
        final_page_rank = {}
        for page in corpus:
            rank = (1 - damping_factor) / num_pages
            #loop over pages to see if they link to current page
            for possible_page in corpus:
                links = corpus[possible_page]
                if len(links) == 0:
                    links = corpus.keys()
                if page in links:
                    rank += damping_factor * page_rank[possible_page] / len(links)
                final_page_rank[page] = rank
        
        # Check for convergence
        differences = [abs(final_page_rank[page] - page_rank[page]) for page in corpus]
        if all(diff < 0.001 for diff in differences):
            break
        
        page_rank = final_page_rank.copy()

    # Normalize PageRank values so they sum to 1
    total_rank = sum(page_rank.values())
    
    page_rank = {page: rank/total_rank for page, rank in page_rank.item()}

    return page_rank

[]
if __name__ == "__main__":
    main()
