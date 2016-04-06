import logging
import base64
import hashlib
import hmac
import simplejson
import time

from ckan.common import request
import ckan.lib.helpers as h
import ckan.plugins as p

log = logging.getLogger(__name__)


class DgvatXlsExport(p.SingletonPlugin):
    """
    Insert javascript fragments into package pages and the home page to
    allow users to view and create comments on any package.
    """
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes)     

    def before_map(self, map):
        map.connect('export', '/export_xls', controller='ckanext.dgvat_xls.controllers.export:DgvatExportController', action='export_xls')
        return map
    
    
    def after_map(self, map):
        return map

    def update_config(self, config):
        # add template directory to template path
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_template_directory(config, 'public')