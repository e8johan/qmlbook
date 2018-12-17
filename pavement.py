from paver.easy import *
from livereload import Server, shell


@task
@needs('assets_init', 'build_html', 'build_pdf', 'build_epub', 'build_qt', 'build_assets')
def build_all():
    pass


@task
@needs('build_all')
def build_deploy():
    with pushd('docs'):
        with pushd('assets'):
            excludelist = [ './index.rst', './examples-list.txt' ]
            for f in filter(lambda x: x not in excludelist, path('.').files('*')):
                path(f).copy('../../_build/html/assets')

@task
@needs('build_assets')
def build_html():
    sh('make html')


@task
def build_pdf():
    pass # needs to be fixed
#    sh('make latexpdf')
#    path('_build/latex/qt5_cadaques.pdf').copy('docs/assets')


@task
def build_epub():
    pass # needs to be fixed
#    sh('make epub')
#    path('_build/epub/qt5_cadaques.epub').copy('docs/assets')


@task
def build_qt():
    pass # needs to be fixed
#    sh('export QTHELP=True; make qthelp')
#    sh('qcollectiongenerator _build/qthelp/Qt5CadaquesBook.qhcp')
#    path('_build/qthelp/Qt5CadaquesBook.qch').copy('docs/assets')


@task
@needs('build_qt')
def show_qt():
    sh('assistant -collectionFile _build/qthelp/Qt5CadaquesBook.qch')


@task
def clean():
    sh('make clean')
    with pushd('docs'):
        path('assets').rmtree()


@task
def shoot():
    for doc in path('.').walkfiles('screenshots.qml'):
        with pushd(doc.dirname()):
            sh('shorty screenshots.qml')


@task
def serve():
    with pushd('_build/html'):
        sh('python -m SimpleHTTPServer')


@task
@needs('build_html')
def live():
    server = Server()
    server.watch('en', shell('paver build_html', cwd='.'))
    server.serve(root='_build/html', open_url_delay=True)


@task
def assets_init():
    with pushd('docs'):
        path('assets').makedirs()
    path('assets/index.rst').copy('docs/assets')


@task
@needs('assets_init')
def build_assets():
    with pushd('docs'):
        
        chapters = [ 'meetqt',
                     'start',
                     'qtcreator',
                     'qmlstart',
                     'fluid',
                     'modelview',
                     'canvas',
                     'particles',
                     'shaders',
                     'multimedia',
                     'networking',
                     'storage',
                     'dynamicqml',
                     'javascript',
                     'qtcpp',
                     'extensions' ]
        
        examples = []
        for c, n in enumerate(chapters, 1):
            name = '%s-%s-assets.tgz' % ( ("00" + str(c))[-2:], n)
            ch = path('.').dirs(n)[0]
            if ch.joinpath('src').isdir():
                examples.append((c, name))
                sh('tar czf assets/{0} --exclude=".*" {1}/src/'.format(name, n))
                
        f = open('examples-list.txt', 'w')
        g = open('assets/examples-list.txt', 'w')
        for c, n in examples:
            f.write("* `Chapter %s examples (%s) <%s>`_\n" % (c, n, "assets/" + n))
            g.write("* `Chapter %s examples (%s) <%s>`_\n" % (c, n, n))
        f.close()
        g.close()
        
@task
@needs('build_all')
def publish():
    with pushd('../qmlbook.github.io'):
        sh('git pull')
        sh('git checkout master')
        sh('cp -rf ../qmlbook/_build/html/* .')
        sh('cp -rf ../qmlbook/assets .')
        sh('git add .')
        sh('git commit -m "update"')
        sh('git push')
