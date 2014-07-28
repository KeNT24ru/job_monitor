# Data mining config
CAT_WHITE_LIST = {
    'odesk': (
        'Web Development',
        'Software Development',
    ),
    'elance': (
        'IT & Programming',
    ),
}
TITLE_KEY_BLACK_LIST = (
    'php',
    'axapta',
    'asp.net',
    'java',
    'wordpress',
    'vb.net',
    'drupal',
    'prestashop',
    'nodejs',
    'node.js',
    'openerp',
)

COMMON_KEY_BLACK_LIST = (
    'majento',
    'magento',
) + TITLE_KEY_BLACK_LIST

# Too noizy
# 'statistics',

QUERY_LIST = (
    # data processing
    ('analyzing data', 'data mining'),
    ('data analysis', 'data mining'),
    ('data analytics', 'data mining'),
    ('data extraction', 'data mining'),
    ('data import', 'data mining'),
    ('data mine', 'data mining'),
    ('data mining', 'data mining'),
    ('data science', 'data mining'),
    ('graph database', 'data mining'),
    ('import data', 'data mining'),
    ('load data', 'data mining'),
    ('machine learning', 'data mining'),
    ('machine vision', 'data mining'),
    ('mapreduce', 'data mining'),
    ('natural language processing', 'data mining'),
    ('neo4j', 'data mining'),
    ('nlp', 'data mining'),
    ('process data', 'data mining'),
    ('extract data', 'data mining'),
    ('future telling', 'data mining'),
    ('predictive platform', 'data mining'),
    ('analytics platform', 'data mining'),
    ('data relationship', 'data mining'),
    # computer vision
    ('opencv', 'computer vision'),
    ('visualization', 'computer vision'),
    # web scraping
    ('crawler', 'web scraping'),
    ('scraper', 'web scraping'),
    ('scrapper', 'web scraping'),
    ('scraping', 'web scraping'),
    ('scrapping', 'web scraping'),
    ('screen scrape', 'web scraping'),
    ('site scraped', 'web scraping'),
    # python, django
    ('python', 'python'),
    ('django', 'python'),
    ('flask', 'python'),
    # startup
    ('startup', 'start-up'),
    ('start-up', 'start-up'),
    # mongodb
    ('mongodb', 'mongodb'),
)
