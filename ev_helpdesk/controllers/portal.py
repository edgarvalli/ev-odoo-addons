from odoo.http import Controller, route, request


class PortalController(Controller):
    @route(
        "/helpdesk/portal",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def portal_index(self):

        ticket = request.env["ev.helpdesk.ticket"].browse(1)

        values = {
            "session_info": request.env["ir.http"].get_frontend_session_info(),
            "language_selector_visible": False,
            "ticket": ticket,
        }

        return request.render("ev_helpdesk.ev_helpdesk_portal", values)
