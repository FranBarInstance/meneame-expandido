# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-pwa-py (See LICENCE)

"""Dispatcher for Resumen IA."""

from core.dispatcher import Dispatcher


class DispatcherResumen(Dispatcher):
    """Dispatcher for Resumen IA."""

    def set_resumen_name(self, component_schema, resumen_name=None) -> bool:
        """Set Resumen name."""

        if resumen_name is None:
            self.schema_data['resumen_name'] = ''
            return True

        if resumen_name not in component_schema['inherit']['data']['resumen_urls']:
            self.schema_data['resumen_name'] = ''
            return False

        self.schema_data['resumen_name'] = resumen_name
        return True
