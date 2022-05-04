from enum import Enum


class CACode(Enum):
    ACTION_CANCEL = "ACTION_CANCEL"


class AnalyzerClientAction:
    """Analyzer Client Action handler, used by the client to dispatch actions
    and for the analyzer process to listen to any dispatched actions.

    """
    def __init__(self):
        self.current_action = None

    def dispatch(self, action: CACode) -> None:
        """Dispatch an action.

        :param action: The action to dispatch.
        :trype action: CACode

        :return: None
        """
        self.current_action = action

    def get_state(self) -> CACode:
        """Get state of current action without popping (and resetting) it.

        :return: The state of the current action.
        :rtype: CACode
        """
        return self.current_action

    def pop_state(self) -> CACode:
        """Get state of current action and reset it.

        :return: The state of the current action.
        :rtype: CACode
        """
        current_state = self.current_action
        self.current_action = None
        return current_state
