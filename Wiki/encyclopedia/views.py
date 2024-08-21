from django.shortcuts import redirect, render
from markdown2 import Markdown
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title):
    if util.get_entry(title) is None:
        return render(request, "encyclopedia/404.html")
    else:
        markdowner = Markdown()
        htmltext = markdowner.convert(util.get_entry(title))
        return render(request, "encyclopedia/title.html", {
            "html": htmltext,
            "title": title
        })

def search(request):
    if request.method == 'POST':
        query = request.POST["q"]
        if util.get_entry(query) is not None:
            return redirect('title', title=query)
        else:
            article_list = [article for article in util.list_entries() if query.lower() in article.lower()]
            if len(article_list) == 0:
                return render(request, "encyclopedia/notfound.html", {
                    "query": query
                })
            else:
                return render(request, "encyclopedia/search.html", {
                    "entries": article_list,
                    "query": query
                })
    else:
        return redirect('index')

def create(request):
    if request.method == 'GET':
        return render(request, "encyclopedia/create.html")
    else:
        title = request.POST["title"]
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/exists.html", {
                "title": title
            })
        else:
            util.save_entry(title, request.POST["body"])
            return redirect('title', title=title)

def edit(request, title):
    if request.method == 'GET':
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "body": util.get_entry(title)
        })
    else:
        util.save_entry(title, request.POST["body"])
        return redirect('title', title=title)

def randomp(request):
    title = random.choice(util.list_entries())
    return redirect('title', title=title)
