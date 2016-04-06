# -*- coding: utf-8 -*- 
import logging
import os

import ckan.lib.base as base
import ckan.model as model
import ckan.lib.render
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.mailer as mailer
import ckan.lib.helpers as h

import pylons.config as config

import ckanext.dgvat_form.lib.dgvat_helper as dgvat_helper

from xlrd import open_workbook
from xlwt import Workbook
from xlutils.copy import copy

render = base.render

from ckan.common import json, request, c, g, response

log = logging.getLogger(__name__)

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

class DgvatExportController(base.BaseController):

    def export_xls(self):
        user = model.User.get('admin')
        context = {'model':model,'user': user,'session':model.Session}
        log.fatal(c.user)
        
        dd = {'permission': 'create_dataset'}
        con = {'user': c.user}
        orgs = logic.get_action('organization_list_for_user')(con, dd)
        c.organization = orgs[0]
        log.fatal(orgs[0])
        c.orgs = orgs

        
        if request.params.get('sent'):
            c.sent = request.params.get('sent')
            print "all?"
            c.all = request.params.get('all') or 0
            print c.all
            print request.params.get('all')
            if c.all == "1":
                dd = {}
                search = logic.get_action('package_search')(con, dd)
                print search
                packages = []
                count = search.get("count")
                start = 0
                while count > 0:
                    dd["rows"] = 1000
                    dd["start"] = start
                    #dd["sort"] = "organization"
                    list = logic.get_action('package_search')(con, dd)
                    packages += list.get("results")
                    count -= 1000
                    start += 1000
                print packages
                filename = "all"
            else:
                dd = {'id': request.params.get('owner_org')}
                group_dict = logic.get_action('organization_show')(con, dd)
                packages = group_dict.get("packages")
                filename = group_dict['name']

            template = config.get('export_xls.template')
            rb = open_workbook(template)
            wb = copy(rb)

            i = 1
            j = 0
            for pkg_dict in packages:
                if(pkg_dict.get("type") == "dataset"):
                    print pkg_dict
                    row = i + 7
                    s = wb.get_sheet(0)
                    d = wb.get_sheet(1)
                    s.write(row, 0, i)
                    s.write(row, 1, pkg_dict["id"])
                    s.write(row, 2, pkg_dict.get("metadata_modified", "").split("T")[0])
                    s.write(row, 3, pkg_dict["title"])
                    s.write(row, 4, pkg_dict["notes"])
                    s.write(row, 5, self.get_categories(pkg_dict))
                    s.write(row, 6, self.get_tags(pkg_dict))
                    s.write(row, 7, pkg_dict["maintainer"])
                    s.write(row, 8, pkg_dict["license_title"])
                    
                    s.write(row, 9, self.get_extra_field("begin_datetime", pkg_dict))

                    s.write(row, 10, self.get_extra_field("publisher", pkg_dict))

                    s.write(row, 11, self.get_extra_field("schema_name", pkg_dict))
                    s.write(row, 12, self.get_extra_field("schema_language", pkg_dict))
                    s.write(row, 13, self.get_extra_field("schema_characterset", pkg_dict))
                    s.write(row, 14, self.get_extra_field("metadata_linkage", pkg_dict))
                    s.write(row, 15, self.get_extra_field("attribute_description", pkg_dict))
                    s.write(row, 16, self.get_extra_field("maintainer_link", pkg_dict))
                    s.write(row, 17, self.get_extra_field("geographic_toponym", pkg_dict))
                    s.write(row, 18, self.get_extra_field("geographic_bbox", pkg_dict))
                    s.write(row, 19, self.get_extra_field("end_datetime", pkg_dict))
                    s.write(row, 20, self.get_extra_field("update_frequency", pkg_dict))
                    s.write(row, 21, self.get_extra_field("lineage_quality", pkg_dict))
                    s.write(row, 22, self.get_extra_field("en_title_and_desc", pkg_dict))
                    s.write(row, 23, self.get_extra_field("license_citation", pkg_dict))
                    s.write(row, 24, self.get_extra_field("metadata_origin_portal", pkg_dict))
                    s.write(row, 25, pkg_dict["maintainer_email"] or self.get_extra_field("maintainer_email", pkg_dict))

                    
                    for res in pkg_dict.get("resources"):
                        print res
                        res_row = j + 8
                        d.write(res_row, 0, i)
                        d.write(res_row, 1, res.get("url"))
                        d.write(res_row, 2, res.get("format"))
                        d.write(res_row, 3, res.get("name"))
                        created = res.get("created") or " T "
                        d.write(res_row, 4, created.split("T")[0])
                        last_modified = res.get("last_modified") or res.get("created") or " T "
                        d.write(res_row, 5, last_modified.split("T")[0])
                        d.write(res_row, 6, res.get("size"))
                        d.write(res_row, 7, res.get("language"))
                        d.write(res_row, 8, res.get("encoding"))
                        j = j + 1
                    i = i + 1
            
            filepath = config.get('export_xls.path')
            ensure_dir(filepath)
            filepath = filepath + filename + '.xls'
            wb.save(filepath)         
            c.path = h.url_for_static(config.get('dgvat_xls.url', '/exportFiles/') + filename + '.xls')
        else:
            c.sent = 0
        return base.render('home/export.html')   

    def get_extra_field(self, name, pkg):
        for field in pkg.get("extras", []):
            if field.get("key") == name:
                if name == "update_frequency":
                    if field.get("value") != "" and field.get("value") != "null":
                        return dgvat_helper.get_update_frequency_by_id(field.get("value"))
                    else:
                        return ""
                if name == "begin_datetime":
                    return field.get("value").split("T")[0]
                return field.get("value")
        return None

    def get_categories(self, pkg):
        for field in pkg.get("extras", []):
            if field.get("key") == "categorization":
                cats = field.get("value", "")
                s  = ""
                if isinstance(cats, basestring):
                    for c in cats.split(","):
                        print c
                        
                        c = c.replace(' ', '').replace('{', '').replace('}','').replace('[', '').replace(']','').replace('"', '').replace("u'", '').replace("'", '')
                        if c.startswith("u'"):
                            c = c[2:-1]
                        if dgvat_helper.get_categorization_by_id(c):
                            s += dgvat_helper.get_categorization_by_id(c)
                        s += ', '
                    return s[:-2]
                else:
                    for c in cats:
                        if dgvat_helper.get_categorization_by_id(c):
                            s += dgvat_helper.get_categorization_by_id(c)
                        s += ', '
                    return s[:-2]
        return ""


    def get_tags(self, pkg):
        s = ""
        for tag in pkg.get("tags", []):
            s += tag.get("display_name")
            s += ", "
        return s[:-2]