from .admin_panel.administrator import AdministratorHandler
from .admin_panel.postcard.category import CategoryHandler
from .admin_panel.postcards import AdminPanelPostCardsHandler
from .admin_panel.stats import StatsHandler
from .admin_panel.users import AdminPanelUsersHandler
from .main_menu import MainMenuHandler
from .settings import SettingsHandler

__all__ = [
    MainMenuHandler,
    SettingsHandler,
    StatsHandler,
    AdministratorHandler,
    CategoryHandler,
    AdminPanelUsersHandler,
    AdminPanelPostCardsHandler,
]
