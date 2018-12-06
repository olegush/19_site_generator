from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import os
from markdown2 import Markdown
from slugify import slugify
import time


def load_data(filepath):
    with open(filepath, encoding="utf8") as file:
        return json.loads(file.read())


def get_env():
    return Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html'])
    )


def get_articles_list_with_paths(articles_list, file_ext):
    articles = articles_list.copy()
    for article in articles:
        source = article['source'].split('/')
        article['dir_name'] = source[0]
        article['filename'] = slugify(source[1].replace('.md', '')) + file_ext
    return sorted(articles, key=lambda x: x['title'])


def write_index_file(template, topics, articles):
    template_index = get_env().get_template(template)
    index_str = template_index.render(topics=topics, articles=articles)
    with open('docs/index.html', mode='w', encoding='utf-8') as file_index:
        file_index.write(index_str)


def get_html_data(dir_articles, path, markdowner):
    with open(
        os.path.join(dir_articles, path),
        encoding='utf-8'
    ) as file_md:
        md_data = file_md.read()
    return markdowner.convert(md_data)


def write_article_file(path, filename, article_str):
    if not os.path.isdir(path):
        os.mkdir(path)
    with open(
        os.path.join(path, filename),
        mode='w',
        encoding='utf-8'
    ) as file_article:
        file_article.write(article_str)


def write_articles_files(path, template, topics, articles):
    template_article = get_env().get_template(template)
    markdowner = Markdown()
    for topic in topics:
        for article in filter(lambda x: x['topic'] == topic['slug'], articles):
            path_to_articles_dir = os.path.join(path, article['dir_name'])
            article_html = get_html_data(
                'articles',
                article['source'],
                markdowner
            )
            article_str = template_article.render(
                topic_title=topic['title'],
                article_title=article['title'],
                article_content=article_html
            )
            write_article_file(
                path_to_articles_dir,
                article['filename'],
                article_str
            )


if __name__ == '__main__':
    start_time = time.time()
    data_for_site = load_data('config.json')
    topics = sorted(data_for_site['topics'], key=lambda x: x['title'])
    articles = get_articles_list_with_paths(data_for_site['articles'], '.html')
    print('Data loaded and formatted')
    write_index_file('index.html', topics, articles)
    print('Index.html created')
    write_articles_files('docs/articles', 'article.html', topics, articles)
    print('{} Articles on {} topics were created in {:.2f} seconds'.format(
        len(articles),
        len(topics),
        time.time() - start_time
    ))
