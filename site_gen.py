from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import os
from markdown2 import Markdown
import re
import time


def load_data(filepath):
    with open(filepath, encoding="utf8") as file:
        return json.loads(file.read())


def get_env():
    return Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html'])
    )


def get_new_articles_list(articles_list):
    articles = []
    for article in sorted(articles_list, key=lambda x: x['title']):
        article['path'] = re.sub(
            '[^0-9a-z_/.-]',
            '',
            article['source']
        ).replace('.md', '.html')
        articles.append(article)
    return articles


def write_index_file(template, topics, articles):
    template_index = get_env().get_template(template)
    index_str = template_index.render(topics=topics, articles=articles)
    with open('docs/index.html', mode='w', encoding='utf-8') as file:
        file.write(index_str)


def get_md_data(dir, path):
    with open(
        os.path.join(dir, path),
        encoding='utf-8'
    ) as file:
        return file.read()


def write_article_file(path, filename, filext, article_str):
    if not os.path.isdir(path):
        os.mkdir(path)
    with open(
        os.path.join(path, filename + filext),
        mode='w',
        encoding='utf-8'
    ) as file:
        file.write(article_str)


def write_articles_files(template, topics, articles):
    template_article = get_env().get_template(template)
    markdowner = Markdown()
    for topic in topics:
        for article in articles:
            if article['topic'] in topic['slug']:
                dir, full_filename = os.path.split(article['path'])
                filename, filext = os.path.splitext(full_filename)
                path_to_articles_dir = os.path.join('docs/articles', dir)
                article_md = get_md_data('articles', article['source'])
                article_str = template_article.render(
                    url=article['path'],
                    topic_title=topic['title'],
                    article_title=article['title'],
                    article_content=markdowner.convert(article_md)
                )
                write_article_file(
                    path_to_articles_dir,
                    filename,
                    filext,
                    article_str
                )


if __name__ == '__main__':
    start_time = time.time()
    data_for_site = load_data('config.json')
    topics = sorted(data_for_site['topics'], key=lambda x: x['title'])
    articles = get_new_articles_list(data_for_site['articles'])
    print('Data loaded and formatted')
    write_index_file('index.html', topics, articles)
    print('Index.html created')
    write_articles_files('article.html', topics, articles)
    print('Articles created')
    print('{:.2f} seconds'.format(time.time() - start_time))
