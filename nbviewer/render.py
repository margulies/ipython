#-----------------------------------------------------------------------------
#  Copyright (C) 2013 The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from tornado.log import app_log
from IPython.nbformat.current import reads_json
from IPython.nbconvert.exporters import Exporter

#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------

class NbFormatError(Exception):
    pass

exporters = {}

def render_notebook(exporter, json_notebook, url=None, forced_theme=None, config=None):
    app_log.info("rendering %d B notebook from %s", len(json_notebook), url)
    if not isinstance(exporter, Exporter):
        # allow exporter to be passed as a class, rather than instance
        # because Exporter instances cannot be passed across multiprocessing boundaries
        # instances are cached by class to avoid repeated instantiation of duplicates
        exporter_cls = exporter
        if exporter_cls not in exporters:
            app_log.info("instantiating %s" % exporter_cls.__name__)
            exporters[exporter_cls] = exporter_cls(config=config, log=app_log)
        exporter = exporters[exporter_cls]
    
    try:
        nb = reads_json(json_notebook)
    except ValueError:
        raise NbFormatError('Error reading JSON notebook')


    css_theme = nb.get('metadata', {}).get('_nbviewer', {}).get('css', None)

    if not css_theme or not css_theme.strip():
        # whitespace
        css_theme = None

    if forced_theme:
        css_theme = forced_theme

    # get the notebook title, if any
    try:
        name = nb.metadata.name
    except AttributeError:
        name = ''
    
    if not name and url is not None:
        name = url.rsplit('/')[-1]

    if not name.endswith(".ipynb"):
        name = name + ".ipynb"
    
    html, resources = exporter.from_notebook_node(nb)

    config = {
            'download_name': name,
            'css_theme': css_theme,
            }
    return html, config