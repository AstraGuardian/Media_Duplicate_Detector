"""
Widget-specific styling functions for themed widgets.

Each function configures ttk widget styles for a given color palette.
"""

from tkinter import ttk
from themes.theme_config import SPACING


def apply_button_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure button styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    # Default button style (secondary)
    config = {
        'background': palette['bg_elevated'],
        'foreground': palette['text_primary'],
        'borderwidth': 1,
        'relief': 'flat',
        'padding': (SPACING['md'], SPACING['sm'])  # 12px horizontal, 8px vertical
    }
    if fonts:
        config['font'] = fonts['body']

    style.configure('TButton', **config)

    # State-based styling for default buttons
    style.map('TButton',
        background=[
            ('active', palette['bg_hover']),
            ('pressed', palette['bg_secondary']),
            ('disabled', palette['bg_secondary'])
        ],
        foreground=[('disabled', palette['text_disabled'])],
        bordercolor=[
            ('focus', palette['border_focus']),
            ('!focus', palette['border_default'])
        ]
    )

    # Primary button style (for main actions like Scan)
    style.configure('Primary.TButton',
        background=palette['accent_primary'],
        foreground='#ffffff',
        borderwidth=0,
        relief='flat',
        padding=(SPACING['md'], SPACING['sm'])
    )
    if fonts:
        style.configure('Primary.TButton', font=fonts['body'])

    style.map('Primary.TButton',
        background=[
            ('active', '#0086d6'),  # Lighter blue on hover
            ('pressed', '#005a9e'),  # Darker blue when pressed
            ('disabled', palette['bg_secondary'])
        ],
        foreground=[('disabled', palette['text_disabled'])]
    )

    # Danger button style (for Delete)
    style.configure('Danger.TButton',
        background=palette['accent_danger'],
        foreground='#ffffff',
        borderwidth=0,
        relief='flat',
        padding=(SPACING['md'], SPACING['sm'])
    )
    if fonts:
        style.configure('Danger.TButton', font=fonts['body'])

    style.map('Danger.TButton',
        background=[
            ('active', '#ff9d8a'),  # Lighter red on hover
            ('pressed', '#d96e5d'),  # Darker red when pressed
            ('disabled', palette['bg_secondary'])
        ],
        foreground=[('disabled', palette['text_disabled'])]
    )


def apply_frame_styles(style: ttk.Style, palette: dict):
    """
    Configure frame styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
    """
    style.configure('TFrame',
        background=palette['bg_primary']
    )


def apply_label_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure label styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    config = {
        'background': palette['bg_primary'],
        'foreground': palette['text_primary']
    }
    if fonts:
        config['font'] = fonts['body']
    style.configure('TLabel', **config)

    # Header variant for larger text
    if fonts:
        style.configure('Header.TLabel',
            background=palette['bg_primary'],
            foreground=palette['text_bright'],
            font=fonts['header']
        )


def apply_treeview_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure treeview styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    config = {
        'background': palette['bg_tertiary'],
        'foreground': palette['text_primary'],
        'fieldbackground': palette['bg_tertiary'],
        'borderwidth': 0,
        'relief': 'flat'
    }
    if fonts:
        config['font'] = fonts['body']
    style.configure('Treeview', **config)

    # Heading style
    heading_config = {
        'background': palette['bg_secondary'],
        'foreground': palette['text_bright'],
        'borderwidth': 1,
        'relief': 'flat'
    }
    if fonts:
        heading_config['font'] = fonts['body']
    style.configure('Treeview.Heading', **heading_config)

    # State-based styling
    style.map('Treeview',
        background=[('selected', palette['selection_bg'])],
        foreground=[('selected', palette['text_bright'])]
    )

    style.map('Treeview.Heading',
        background=[('active', palette['bg_hover'])]
    )


def apply_notebook_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure notebook (tabbed interface) styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    style.configure('TNotebook',
        background=palette['bg_primary'],
        borderwidth=0
    )

    # Tab styling
    tab_config = {
        'background': palette['bg_secondary'],
        'foreground': palette['text_secondary'],
        'padding': (SPACING['lg'], SPACING['sm']),  # 16px horizontal, 8px vertical
        'borderwidth': 0
    }
    if fonts:
        tab_config['font'] = fonts['body']
    style.configure('TNotebook.Tab', **tab_config)

    # Active tab gets accent color underline effect via background
    style.map('TNotebook.Tab',
        background=[
            ('selected', palette['bg_primary']),
            ('active', palette['bg_hover'])
        ],
        foreground=[
            ('selected', palette['text_bright']),
            ('active', palette['text_primary'])
        ],
        expand=[('selected', [1, 1, 1, 2])]  # Add bottom border effect
    )


def apply_entry_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure entry (text input) styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    config = {
        'fieldbackground': palette['bg_secondary'],
        'foreground': palette['text_primary'],
        'borderwidth': 1,
        'relief': 'solid',
        'bordercolor': palette['border_default'],
        'lightcolor': palette['border_default'],
        'darkcolor': palette['border_default']
    }
    if fonts:
        config['font'] = fonts['body']
    style.configure('TEntry', **config)

    style.map('TEntry',
        bordercolor=[('focus', palette['border_focus'])],
        lightcolor=[('focus', palette['border_focus'])],
        darkcolor=[('focus', palette['border_focus'])]
    )


def apply_scale_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure scale (slider) styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    config = {
        'background': palette['bg_primary'],
        'troughcolor': palette['bg_secondary'],
        'borderwidth': 0,
        'sliderrelief': 'flat'
    }
    if fonts:
        config['font'] = fonts['small']
    style.configure('TScale', **config)


def apply_scrollbar_styles(style: ttk.Style, palette: dict):
    """
    Configure scrollbar styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
    """
    style.configure('TScrollbar',
        background=palette['bg_secondary'],
        troughcolor=palette['bg_primary'],
        borderwidth=0,
        arrowcolor=palette['text_secondary']
    )

    style.map('TScrollbar',
        background=[
            ('active', palette['bg_hover'])
        ]
    )


def apply_radiobutton_styles(style: ttk.Style, palette: dict, fonts: dict = None):
    """
    Configure radiobutton styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
        fonts: Font configuration dictionary
    """
    config = {
        'background': palette['bg_primary'],
        'foreground': palette['text_primary'],
        'borderwidth': 0
    }
    if fonts:
        config['font'] = fonts['body']
    style.configure('TRadiobutton', **config)

    style.map('TRadiobutton',
        background=[('active', palette['bg_primary'])],
        foreground=[('disabled', palette['text_disabled'])]
    )


def apply_separator_styles(style: ttk.Style, palette: dict):
    """
    Configure separator styles.

    Args:
        style: ttk.Style instance
        palette: Color palette dictionary
    """
    style.configure('TSeparator',
        background=palette['border_default']
    )
