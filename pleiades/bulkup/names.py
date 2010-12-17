
from csv import DictReader
import datetime
import logging
from optparse import OptionParser
import sys

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from pleiades.bulkup import secure, setup_cmfuid

LOG = logging.getLogger('pleiades.bulkup.names')

def bulk_update_names(context, reader, columns, message=None):
    
    catalog = getToolByName(context, 'portal_catalog')
    repo = getToolByName(context, 'portal_repository')
   
    import transaction
    savepoint = transaction.savepoint()
    try:
        for row in reader:
        
            results = catalog(
                path={'query': '/plone' + row['path'], 'depth': 0})
            ob = results[0].getObject()
            
            for key in columns:
                field = ob.getField(key)
                value = row[key]
                field.set(ob, value)

            now = DateTime(datetime.datetime.now().isoformat())
            ob.setModificationDate(now)

            repo.save(ob, message)
            ob.reindexObject()

    except Exception, e:
        savepoint.rollback()
        LOG.error("Rolled back after catching exception: %s" % e)
        import pdb; pdb.set_trace()
    
    transaction.commit()

if __name__ == '__main__':
    # Zopectl doesn't handle command line arguments well, necessitating quoting
    # like this:
    #
    # $ instance run 'names.py -f names.csv -m "Set all descriptions from names-up2.csv again" -j description'
    
    parser = OptionParser()
    parser.add_option(
        "-f", "--file", dest="filename",
        help="Input filename", metavar="FILE")
    parser.add_option(
        "-j", "--columns", dest="columns",
        help="Update columns")
    parser.add_option(
        "-u", "--user", dest="user",
        help="Run script as user")
    parser.add_option(
        "-m", "--message", dest="message",
        help="Version commit message")

    opts, args = parser.parse_args(sys.argv[1:])
    filename = opts.filename
    columns = opts.columns.split(',')

    # Clean up zopectl's argument mess
    if opts.message:
        opts.message = opts.message.replace(', ', ' ')
    message =  opts.message or "Bulk update begun %s" % (
        datetime.datetime.now().isoformat())

    reader = DictReader(open(filename, 'rb'))

    site = app['plone']
    setup_cmfuid(site)
    secure(site, opts.user or 'admin')
    bulk_update_names(site, reader, columns, message)

