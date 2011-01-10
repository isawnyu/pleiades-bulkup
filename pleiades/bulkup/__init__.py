
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFUid.interfaces import IUniqueIdGenerator, \
    IUniqueIdAnnotationManagement, IUniqueIdHandler

from zope.component import provideUtility

def secure(context, username):
    membership = getToolByName(context, 'portal_membership')
    user=membership.getMemberById(username).getUser()
    newSecurityManager(None, user.__of__(context.acl_users))

def setup_cmfuid(context):
    provideUtility(
        getToolByName(context, 'portal_uidgenerator'), IUniqueIdGenerator)
    provideUtility(
        getToolByName(context, 'portal_uidannotation'), 
        IUniqueIdAnnotationManagement)
    provideUtility(
        getToolByName(context, 'portal_uidhandler'), IUniqueIdHandler)


