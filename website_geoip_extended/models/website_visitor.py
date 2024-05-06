from odoo import models, fields
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'

    # Ajout de champs supplémentaires pour collecter plus d'informations sur le visiteur
    region = fields.Char("Region")
    postal_code = fields.Char("Postal Code")
    latitude = fields.Float("Latitude")
    longitude = fields.Float("Longitude")
    ip_address = fields.Char("IP Address")
    isp = fields.Char("Internet Service Provider")
    connection_type = fields.Char("Connection Type")
    device_type = fields.Char("Device Type")
    operating_system = fields.Char("Operating System")
    browser = fields.Char("Browser")

    def _upsert_visitor(self, access_token, force_track_values=None):
        # Logger les informations de la requête
        _logger.info('Request Remote Address: %s', request.httprequest.remote_addr)
        _logger.info('User Agent: %s', request.httprequest.user_agent.string)

        # Obtenez les données de GeoIP et d'autres sources
        geoip_info = request.httprequest.environ.get('geoip', {})
        user_agent = request.httprequest.user_agent

        _logger.debug('geoip_info: %s', geoip_info)

        _logger.info('User Agent Details: Platform: %s, Browser: %s, Version: %s', user_agent.platform, user_agent.browser, user_agent.version)

        # _logger.info('User Agent Details: OS: %s, Browser: %s, Device: %s', user_agent.os, user_agent.browser, user_agent.platform)

        # Appel de la méthode parente via super()
        visitor_id, upsert_type = super()._upsert_visitor(access_token, force_track_values)

        # Récupération du visiteur basé sur l'ID retourné
        visitor = self.browse(visitor_id)

        # Mise à jour du visiteur avec les nouvelles données
        update_values = {
            'region': geoip_info.get('region'),
            'postal_code': geoip_info.get('postal_code'),
            'latitude': geoip_info.get('latitude'),
            'longitude': geoip_info.get('longitude'),
            'ip_address': request.httprequest.remote_addr,
            'isp': geoip_info.get('isp'),
            'connection_type': geoip_info.get('connection_type'),
            'device_type': user_agent.platform,
            'operating_system': user_agent.platform,  # Modifié pour utiliser platform
            'browser': user_agent.browser,
        }
        _logger.info('Updating Visitor with: %s', update_values)

        visitor.sudo().write(update_values)

        return visitor_id, upsert_type
