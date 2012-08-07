from zope.i18nmessageid import MessageFactory

portletPloneboardMessageFactory = MessageFactory("collective.portlet.ploneboard")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""