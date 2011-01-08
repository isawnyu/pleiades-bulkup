
from csv import DictReader
import datetime
import logging
from optparse import OptionParser
import sys

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from pleiades.bulkup import secure, setup_cmfuid

LOG = logging.getLogger('pleiades.bulkup.locations')

def bulk_update_locations(context, reader, columns, message=None):

    catalog = getToolByName(context, 'portal_catalog')
    repo = getToolByName(context, 'portal_repository')
   
    import transaction
    savepoint = transaction.savepoint()
    try:
        for row in reader:
        
            path = '/plone' + row['path']
            results = catalog(
                path={'query': path, 'depth': 0})

            if not results:
                # create a location in the place
                # TODO: implement
                pid = path.split('/')[3]
                place = context['places'][pid]
                place.invokeFactory(
                    'Location',
                    row['id'],
                    title=row['title'], 
                    geometry=row['geometry'],
                    creators=row['creators'],
                    contributors='R. Talbert, T. Elliott, S. Gillies')

            else:
                # update
                try:
                    ob = results[0].getObject()
                except IndexError:
                    LOG.warn("Not found, cannot update %s" % path)
                    continue

                for key in columns:
                    field = ob.getField(key)
                    value = row[key]

                    if key == 'geometry':
                        ob.setGeometry(value)
                    else:
                        field.set(ob, value)

                now = DateTime(datetime.datetime.now().isoformat())
                ob.setModificationDate(now)

                repo.save(ob, message)
                ob.reindexObject()

    except Exception, e:
        savepoint.rollback()
        LOG.error("Rolled back after catching exception: %s" % e)
    
    transaction.commit()
    context._p_jar.sync()
    
    # end

if __name__ == '__main__':
    # Zopectl doesn't handle command line arguments well, necessitating quoting
    # like this:
    #
    # $ instance run 'locations.py -f locations.csv -m "Set all descriptions from names-up2.csv again" -j description'
    
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
    bulk_update_locations(site, reader, columns, message)

