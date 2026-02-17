"""Component Resumen IA - Init"""


def init_component(component, component_schema, _schema):
    """Component - Init"""

    route = component['manifest']['route']
    set_local_data(component, component_schema)
    set_menu(route, component['manifest']['config']['resumen_urls'], component_schema)


def set_local_data(component, component_schema):
    """Component - Set Local Data"""
    resumen_urls = {}
    resumen_valid_names = ''

    for name, url in component['manifest']['config']['resumen_urls'].items():
        if not url:
            continue

        resumen_urls[name] = url
        resumen_valid_names += f"{name}\n"

    component_schema['inherit']['data']['resumen_urls'] = resumen_urls
    component_schema['inherit']['data']['resumen_valid_names'] = resumen_valid_names


def set_menu(route, resumen_urls, component_schema):
    """Component - Set Menu"""

    # Get root menu items from inherited data
    base_menu = component_schema['inherit']['data']['menu']
    menu_session_root = base_menu['session:']['resumen']['root']
    menu_session_true_root = base_menu['session:true']['resumen']['root']

    menu = {
        'session:': {
            'resumen': {
                'root': menu_session_root
            }
        },
        'session:true': {
            'resumen': {
                'root': menu_session_true_root
            }
        }
    }

    # create menu items
    for name, url in resumen_urls.items():
        if not url:
            continue
        menu_item = {
            'text': name,
            'link': f'{route}/site/{name}',
            'icon': 'x-icon-agent',
            'class': 'click-load-spin'
        }
        menu['session:']['resumen'][name] = menu_item
        menu['session:true']['resumen'][name] = menu_item

    # set menu in local data
    component_schema['inherit']['data']['menu'] = menu
