from odoo import http
from odoo.http import request
import json

class ExtendedWebManifest(http.Controller):

    @http.route('/web/manifest.webmanifest', type='http', auth='public', methods=['GET'])
    def webmanifest(self):
        # Fetch the company of the current user
        company = request.env.user.company_id

        # Generate the manifest using company-specific settings
        manifest = {
            'name': company.name,  # Consider adding a specific field in res.company if a different name is needed
            'background_color': company.web_app_bgcolor or '#714B67',  # Default value if not set
            'theme_color': company.web_app_fgcolor or '#FFFFFF',  # Default value if not set
            'icons': [
                {
                    'src': f'/web/image?model=res.company&id={company.id}&field=web_app_icon',
                    'sizes': '192x192',
                    'type': 'image/png'
                },
                {
                    'src': f'/web/image?model=res.company&id={company.id}&field=pwa_icon_192',
                    'sizes': '192x192',
                    'type': 'image/png'
                },
                {
                    'src': f'/web/image?model=res.company&id={company.id}&field=pwa_icon_512',
                    'sizes': '512x512',
                    'type': 'image/png'
                }
            ],
            'scope': '/web',
            'start_url': '/web',
            'display': 'standalone',
            'prefer_related_applications': False
        }

        # Serialize the manifest into JSON and set the appropriate response headers
        response = request.make_response(json.dumps(manifest), [('Content-Type', 'application/manifest+json')])
        return response
