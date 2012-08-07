from zope.interface import implements
from zope import schema
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.formlib.form import Fields
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from collective.portlet.ploneboard import portletPloneboardMessageFactory as _

from DateTime import DateTime

class IActiveUsersPortlet(IPortletDataProvider):
    """A portlet which shows the most active users in Ploneboard conversations.
    """

    header = schema.TextLine(title=_(u"header",
                                default=u"Portlet title"),
                        required=True,
                        default=u"Active Users")

    num_users = schema.Int(title=_(u"num_users",
                                default=u"Number of users to display"),
                       description=_(u"help_num_users",
                                default=u"How many users to list."),
                       required=True,
                       default=5)
    
    start_date = schema.Int(title=_(u"start_date",
                                default=u"Number of day to count the comments"),
                       description=_(u"help_start_date",
                                default=u"Insert a number of days to count the messages posted by an user in the last x days"),
                       required=True,
                       default=30)


class Assignment(base.Assignment):
    implements(IActiveUsersPortlet)


    def __init__(self, header="", num_users=5,start_date=30):
        self.header=header
        self.num_users=num_users
        self.start_date = start_date
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.header

class Renderer(base.Renderer):
    
    @memoize
    def getUsers(self):
        """return a list of users and the number of comments"""
        pc=getToolByName(self.context, "portal_catalog")
        mtool = getToolByName(self.context, "portal_membership")
        now = DateTime()
        start = now-self.data.start_date
        brains=pc(portal_type="PloneboardComment",created={'query':[start,now],'range':'minmax'})
        users={}
        for brain in brains:
            for creator in brain.listCreators:
                # Check is user exits (manage deleted users)
                if mtool.getMemberById(creator):
                    if users.get(creator,None):
                        users[creator] +=1
                    else:
                        users[creator] = 1
        users_sort = sorted([(x,y) for x,y in users.items()], lambda item1,item2: -2*cmp(item1[1], item2[1]) + cmp(item1[0], item2[0]))
        return users_sort[:self.data.num_users]
    
    def getUserName(self,user):
        """ return fullname of an user, or if it doesn't exist, the userid"""
        pm = getToolByName(self.context, 'portal_membership')
        user_info = pm.getMemberInfo(user)
        if not user_info:
            return user
        if user_info.get('fullname'):
            return user_info.get('fullname')
        else:
            return user
    
    @memoize  
    def getBoardName(self):
        result = self.context.portal_catalog(portal_type='Ploneboard')
        if result:
            return result[0].id
        else:
            return ""
        
    def getSearchUrl(self,user):
        """return the url to make the search of all comments of an user"""
        root_url= '/'.join(self.context.portal_url.getPortalObject().getPhysicalPath())
        board_name= self.getBoardName()
        if board_name:
            url = root_url+'/%s/search?Creator=%s&sort_on=created&sort_order=reverse&portal_type=PloneboardComment'%(board_name,user)
        else:
            url = root_url+'/search?Creator=%s&sort_on=created&sort_order=reverse&portal_type=PloneboardComment'%user
        return url


    @property
    def available(self):
        return True


    @property
    def title(self):
        return self.data.header


    render = ViewPageTemplateFile("active_users.pt")


class AddForm(base.AddForm):
    form_fields = Fields(IActiveUsersPortlet)
    label = _(u"label_add_portlet",
                default=u"Add most Ploneboard active users portlet.")
    description = _(u"help_add_portlet",
            default=u"This portlet shows the most active users.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = Fields(IActiveUsersPortlet)
    label = _(u"label_add_portlet",
                default=u"Add most Ploneboard active users portlet.")
    description = _(u"help_add_portlet",
            default=u"This portlet shows the most active users.")

