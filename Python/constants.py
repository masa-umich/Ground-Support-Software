from PyQt5.QtCore import *
from PyQt5.QtGui import QColor

"""
Class to hold any constant value that is important to the entire program
"""


class Constants:

    GUI_VERSION = 'v2.0.0'

    # Dict of fluids. Example call: fluid["HE"] -> Returns 0
    # TODO: I'm picky so change to LOX
    fluid = {
        "HE" :  0,
        0: "HE",
        "Fuel": 1,
        1: "Fuel",
        "OX":   2,
        2: "OX",
        "LN2":  3,
        3: "LN2",
        "Exhaust": 4,
        4: "Exhaust"
    }

    boards = ["Engine Controller", "Flight Computer", "Pressurization Controller",
              "Recovery Controller", "GSE Controller"]

    line_width = 2 # This is actually overiden lol

    BG_color = QColor(0, 22, 44)
    Board_color = QColor(24, 156, 12, 255)
    Indicator_Green_color = QColor(35, 136, 35, 255)
    Indicator_Yellow_color = QColor(255, 191, 0, 255)
    Indicator_Red_color = QColor(210, 34, 45, 255)
    MASA_Blue_color = QColor(0, 39, 76)
    MASA_Beige_color = QColor(238, 238, 234)
    MASA_Scarlet_color = QColor(242, 46, 0)
    MASA_Maize_color = QColor(255, 203, 5)  # #ffcb05

    default_font = "Montserrat"
    monospace_font = "Roboto Mono"

    # List of fluids
    fluids = ["HE", "Fuel", "OX", "LN2", "Exhaust"]

    # Avionics Objects Prefix List
    object_prefix_map = {
        "Solenoid": "sol.",
        "Tank": "tnk.",
        "Motor": "mtr.",
        "3 Way Valve": "3sol."
    }

    # Dict of fluid colors. Number on left should match value of fluid dict above.
    # Example call: fluidColor[0] -> Returns Qt.white
    fluidColor = {
        "HE": QColor(255,255,255,255),
        0: QColor(255,255,255,255),
        "Fuel": QColor(255,0,0,255),
        1: QColor(255,0,0,255),
        "OX": QColor(0,255,255,255),
        2: QColor(0,255,255,255),
        "LN2": QColor(0,255,0,255),
        3: QColor(0,255,0,255),
        "Exhaust": QColor(255,150,0,255),
        4: QColor(255,150,0,255)
    }

    campaign_data_dir = "data/campaigns/"

    dataHandlerUpdateRate = 200  # ms

    event_lookup = {"0": "QEvent::None",
                    "114": "QEvent::ActionAdded",
                    "113": "QEvent::ActionChanged",
                    "115": "QEvent::ActionRemoved",
                    "99": "QEvent::ActivationChange",
                    "121": "QEvent::ApplicationActivate",
                    "122": "QEvent::ApplicationDeactivate",
                    "36": "QEvent::ApplicationFontChange",
                    "37": "QEvent::ApplicationLayoutDirectionChange",
                    "38": "QEvent::ApplicationPaletteChange",
                    "214": "QEvent::ApplicationStateChange",
                    "35": "QEvent::ApplicationWindowIconChange",
                    "68": "QEvent::ChildAdded",
                    "69": "QEvent::ChildPolished",
                    "71": "QEvent::ChildRemoved",
                    "40": "QEvent::Clipboard",
                    "19": "QEvent::Close",
                    "200": "QEvent::CloseSoftwareInputPanel",
                    "178": "QEvent::ContentsRectChange",
                    "82": "QEvent::ContextMenu",
                    "183": "QEvent::CursorChange",
                    "52": "QEvent::DeferredDelete",
                    "60": "QEvent::DragEnter",
                    "62": "QEvent::DragLeave",
                    "61": "QEvent::DragMove",
                    "63": "QEvent::Drop",
                    "170": "QEvent::DynamicPropertyChange",
                    "98": "QEvent::EnabledChange",
                    "10": "QEvent::Enter",
                    "150": "QEvent::EnterEditFocus",
                    "124": "QEvent::EnterWhatsThisMode",
                    "206": "QEvent::Expose",
                    "116": "QEvent::FileOpen",
                    "8": "QEvent::FocusIn",
                    "9": "QEvent::FocusOut",
                    "23": "QEvent::FocusAboutToChange",
                    "97": "QEvent::FontChange",
                    "198": "QEvent::Gesture",
                    "202": "QEvent::GestureOverride",
                    "188": "QEvent::GrabKeyboard",
                    "186": "QEvent::GrabMouse",
                    "159": "QEvent::GraphicsSceneContextMenu",
                    "164": "QEvent::GraphicsSceneDragEnter",
                    "166": "QEvent::GraphicsSceneDragLeave",
                    "165": "QEvent::GraphicsSceneDragMove",
                    "167": "QEvent::GraphicsSceneDrop",
                    "163": "QEvent::GraphicsSceneHelp",
                    "160": "QEvent::GraphicsSceneHoverEnter",
                    "162": "QEvent::GraphicsSceneHoverLeave",
                    "161": "QEvent::GraphicsSceneHoverMove",
                    "158": "QEvent::GraphicsSceneMouseDoubleClick",
                    "155": "QEvent::GraphicsSceneMouseMove",
                    "156": "QEvent::GraphicsSceneMousePress",
                    "157": "QEvent::GraphicsSceneMouseRelease",
                    "182": "QEvent::GraphicsSceneMove",
                    "181": "QEvent::GraphicsSceneResize",
                    "168": "QEvent::GraphicsSceneWheel",
                    "18": "QEvent::Hide",
                    "27": "QEvent::HideToParent",
                    "127": "QEvent::HoverEnter",
                    "128": "QEvent::HoverLeave",
                    "129": "QEvent::HoverMove",
                    "96": "QEvent::IconDrag",
                    "101": "QEvent::IconTextChange",
                    "83": "QEvent::InputMethod",
                    "207": "QEvent::InputMethodQuery",
                    "169": "QEvent::KeyboardLayoutChange",
                    "6": "QEvent::KeyPress",
                    "7": "QEvent::KeyRelease",
                    "89": "QEvent::LanguageChange",
                    "90": "QEvent::LayoutDirectionChange",
                    "76": "QEvent::LayoutRequest",
                    "11": "QEvent::Leave",
                    "151": "QEvent::LeaveEditFocus",
                    "125": "QEvent::LeaveWhatsThisMode",
                    "88": "QEvent::LocaleChange",
                    "176": "QEvent::NonClientAreaMouseButtonDblClick",
                    "174": "QEvent::NonClientAreaMouseButtonPress",
                    "175": "QEvent::NonClientAreaMouseButtonRelease",
                    "173": "QEvent::NonClientAreaMouseMove",
                    "177": "QEvent::MacSizeChange",
                    "43": "QEvent::MetaCall",
                    "102": "QEvent::ModifiedChange",
                    "4": "QEvent::MouseButtonDblClick",
                    "2": "QEvent::MouseButtonPress",
                    "3": "QEvent::MouseButtonRelease",
                    "5": "QEvent::MouseMove",
                    "109": "QEvent::MouseTrackingChange",
                    "13": "QEvent::Move",
                    "197": "QEvent::NativeGesture",
                    "208": "QEvent::OrientationChange",
                    "12": "QEvent::Paint",
                    "39": "QEvent::PaletteChange",
                    "131": "QEvent::ParentAboutToChange",
                    "21": "QEvent::ParentChange",
                    "212": "QEvent::PlatformPanel",
                    "217": "QEvent::PlatformSurface",
                    "75": "QEvent::Polish",
                    "74": "QEvent::PolishRequest",
                    "123": "QEvent::QueryWhatsThis",
                    "106": "QEvent::ReadOnlyChange",
                    "199": "QEvent::RequestSoftwareInputPanel",
                    "14": "QEvent::Resize",
                    "204": "QEvent::ScrollPrepare",
                    "205": "QEvent::Scroll",
                    "117": "QEvent::Shortcut",
                    "51": "QEvent::ShortcutOverride",
                    "17": "QEvent::Show",
                    "26": "QEvent::ShowToParent",
                    "50": "QEvent::SockAct",
                    "192": "QEvent::StateMachineSignal",
                    "193": "QEvent::StateMachineWrapped",
                    "112": "QEvent::StatusTip",
                    "100": "QEvent::StyleChange",
                    "87": "QEvent::TabletMove",
                    "92": "QEvent::TabletPress",
                    "93": "QEvent::TabletRelease",
                    "171": "QEvent::TabletEnterProximity",
                    "172": "QEvent::TabletLeaveProximity",
                    "219": "QEvent::TabletTrackingChange",
                    "22": "QEvent::ThreadChange",
                    "1": "QEvent::Timer",
                    "120": "QEvent::ToolBarChange",
                    "110": "QEvent::ToolTip",
                    "184": "QEvent::ToolTipChange",
                    "194": "QEvent::TouchBegin",
                    "209": "QEvent::TouchCancel",
                    "196": "QEvent::TouchEnd",
                    "195": "QEvent::TouchUpdate",
                    "189": "QEvent::UngrabKeyboard",
                    "187": "QEvent::UngrabMouse",
                    "78": "QEvent::UpdateLater",
                    "77": "QEvent::UpdateRequest",
                    "111": "QEvent::WhatsThis",
                    "118": "QEvent::WhatsThisClicked",
                    "31": "QEvent::Wheel",
                    "132": "QEvent::WinEventAct",
                    "24": "QEvent::WindowActivate",
                    "103": "QEvent::WindowBlocked",
                    "25": "QEvent::WindowDeactivate",
                    "34": "QEvent::WindowIconChange",
                    "105": "QEvent::WindowStateChange",
                    "33": "QEvent::WindowTitleChange",
                    "104": "QEvent::WindowUnblocked",
                    "203": "QEvent::WinIdChange",
                    "126": "QEvent::ZOrderChange", }
