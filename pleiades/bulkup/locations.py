
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
    pass

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

