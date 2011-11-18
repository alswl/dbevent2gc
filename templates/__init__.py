from web.template import CompiledTemplate, ForLoop, TemplateResult


# coding: utf-8
def error (error):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    self['title'] = join_(u'File Not Found')
    extend_([u'\n'])
    extend_([u'<h1>', escape_(error, True), u'</h1>\n'])

    return self

error = CompiledTemplate(error, 'templates/error.html')
join_ = error._join; escape_ = error._escape

# coding: utf-8
def base (page):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html lang="en" dir="ltr">\n'])
    extend_([u'<head>\n'])
    extend_([u'        <meta charset="utf-8">\n'])
    extend_([u'        <title>', escape_(page.title, True), u'</title>\n'])
    extend_([u'        <link id="css-reset" rel="stylesheet" href="/css/reset.css" type="text/css">\n'])
    extend_([u'        <link id="css-core" rel="stylesheet" href="/css/style.css" type="text/css">\n'])
    extend_([u'        <script src="/js/jquery-1.4.3.min.js"></script>\n'])
    extend_([u'        <script src="/js/app.js"></script>\n'])
    extend_([u'</head>\n'])
    extend_([u'<body>\n'])
    extend_([u'<header>\n'])
    extend_([u'    <h1><a href="/">Demo Todo App</a></h1>      \n'])
    extend_([u'        <nav>\n'])
    extend_([u'                <ul>\n'])
    extend_([u'                        <li><a href="/admin">Home</a></li>\n'])
    extend_([u'                </ul>\n'])
    extend_([u'        </nav>\n'])
    extend_([u'</header>\n'])
    extend_([u'<div id="user">\n'])
    if page.user:
        extend_(['        ', u'    <p>Welcome ', escape_(page.user, True), u' [<a href="', escape_(page.userlogout, True), u'">logout</a>]</p>\n'])
    else:
        extend_(['        ', u'    <p><a href="', escape_(page.userlogin, True), u'">Sign in or register</a></p>\n'])
        extend_(['        ', u'\n'])
    if page.admin:
        extend_(['        ', u'    <p><a href="/_ah/admin/">Admin</a></p>\n'])
        extend_(['        ', u'\n'])
    extend_([u'</div>\n'])
    extend_([u'<div id="main">\n'])
    extend_([u'        <div id="message"></div>\n'])
    extend_([u'        ', escape_(page, False), u'\n'])
    extend_([u'</div>\n'])
    extend_([u'<footer>\n'])
    extend_([u'        <p>Footer</p>\n'])
    extend_([u'</footer>\n'])
    extend_([u'</body>\n'])
    extend_([u'</html>\n'])

    return self

base = CompiledTemplate(base, 'templates/base.html')
join_ = base._join; escape_ = base._escape

# coding: utf-8
def server_error():
    __lineoffset__ = -5
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html lang="en" dir="ltr">\n'])
    extend_([u'<head>\n'])
    extend_([u'        <meta charset="utf-8">\n'])
    extend_([u'        <title>Page Error</title>\n'])
    extend_([u'        <link id="css-reset" rel="stylesheet" href="/css/reset.css" type="text/css">\n'])
    extend_([u'        <link id="css-core" rel="stylesheet" href="/css/style.css" type="text/css">\n'])
    extend_([u'</head>\n'])
    extend_([u'<body>\n'])
    extend_([u'<header>\n'])
    extend_([u'    <h1><a href="/">Demo Todo App</a></h1>      \n'])
    extend_([u'        <nav>\n'])
    extend_([u'                <ul>\n'])
    extend_([u'                        <li><a href="/admin">Admin</a></li>\n'])
    extend_([u'                        <li><a href="/about">About</a></li>\n'])
    extend_([u'                </ul>\n'])
    extend_([u'        </nav>\n'])
    extend_([u'</header>\n'])
    extend_([u'<div id="main">\n'])
    extend_([u'        <h1>An Error Has Occured</h1>\n'])
    extend_([u'</div>\n'])
    extend_([u'</body>\n'])
    extend_([u'</html>\n'])

    return self

server_error = CompiledTemplate(server_error, 'templates/server_error.html')
join_ = server_error._join; escape_ = server_error._escape

# coding: utf-8
def index (items):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'\n'])
    extend_([u'<table id="tasklist">\n'])
    for item in loop.setup(items):
        extend_([u'    <tr><td>', escape_(item.author, True), u'</td><td>', escape_(item.content, True), u'</td><td>', escape_(item.created, True), u'</td></tr>\n'])
    extend_([u'</table>\n'])
    extend_([u'\n'])
    extend_([u'<h2>Add New</h2>\n'])
    extend_([u'<form action="/" method="post">\n'])
    extend_([u'        <p><input type="text" name="content"> <input type="submit" name="add"></p>\n'])
    extend_([u'</form>\n'])

    return self

index = CompiledTemplate(index, 'templates/index.html')
join_ = index._join; escape_ = index._escape

