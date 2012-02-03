#!/usr/bin/env jasy

import shutil


#
# Utils
#

def getSession():
    session = Session()
    session.addProject(Project("../core/"))
    session.addProject(Project("."))

    return session



#
# Tasks
#

@task
def clean():
    logging.info("Clearing cache...")
    session = getSession()
    session.clearCache()
    session.close()



@task
def distclean():
    logging.info("Clearing cache...")
    session = getSession()
    session.clearCache()
    session.close()

    if os.path.exists("build"):
        logging.info("Deleting build folder...")
        shutil.rmtree("build")

@task
def buildcompressed():
    session = getSession()

    for staticFile in [ "index.html", "style.css", "style.small.css" ]:
        updateFile("source/%s" % staticFile, "build/%s" % staticFile)

    # Include all game relevant assets
    resolver = Resolver(session.getProjects())
    resolver.addClassName("api.Browser")
    assets = Asset(session, resolver.getIncludedClasses()).exportBuild()

    # Writing source loader
    classes = Sorter(resolver).getSortedClasses()
    storeCompressed('build/browser.js', classes, bootCode="new api.Browser('../../jukebox/api/data');")

    session.close()


@task
def build():
    session = getSession()

    # Configure permutations
    session.setField("es5", True)
    session.permutateField("debug")

    # Prepare assets
    resolver = Resolver(session.getProjects())
    resolver.addClassName("api.Browser")
    assets = Asset(session, resolver.getIncludedClasses()).exportBuild()
    formatting = Formatting('semicolon', 'comma')

    # Write kernel script
    includedByKernel = storeKernel("build/script/kernel.js", session, assets=assets, formatting=formatting, debug=True)

    # Copy files from source
    for staticFile in [ "index.html", "style.css", "style.small.css" ]:
        updateFile("source/%s" % staticFile, "build/%s" % staticFile)

    # Compiler configuration
    optimization = Optimization("variables", "declarations", "blocks")


    # Process every possible permutation
    for permutation in session.getPermutations():

        # Resolving dependencies
        resolver = Resolver(session.getProjects(), permutation)
        resolver.addClassName("api.Browser")
        resolver.excludeClasses(includedByKernel)

        # Compressing classes
        classes = Sorter(resolver, permutation).getSortedClasses()
        compressedCode = storeCompressed("build/script/browser.js", classes,
            permutation=permutation, optimization=optimization, formatting=formatting, bootCode="new api.Browser();")

    session.close()

 
