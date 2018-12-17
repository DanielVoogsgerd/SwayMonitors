import logging
import json
import os

__all__ = ['Monitor', 'MonitorNode', 'Setup']

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')


class MonitorMode:
    def __init__(self, properties):
        try:
            self.height = properties['height']
            self.width = properties['width']
            self.refresh = properties['refresh']
        except AttributeError:
            raise Exception('MonitorNode is not a valid node')

    # Getters
    def get_dimensions(self) -> tuple:
        return self.width, self.height

    # Check
    def has_dimensions(self, size) -> bool:
        return self.width == size['width'] and self.height == size['height']

    # Private
    def total_pixels(self) -> int:
        return self.width * self.height

    # Magic
    def __gt__(self, other):
        if self.total_pixels() > other.total_pixels():
            return True

        if self.total_pixels() == other.total_pixels() and self.refresh > other.refresh:
            return True

        return False

    def __lt__(self, other):
        if self.total_pixels() < other.total_pixels():
            return True

        if self.total_pixels() == other.total_pixels() and self.refresh < other.refresh:
            return True

        return False

    def __ge__(self, other):
        if not isinstance(other, MonitorMode):
            raise NotImplemented('Comparing MonitorNodes to non-MonitorNodes is not supported (yet)')

        # You might want to do this with total ordering
        return self.__eq__(other) or self.__gt__(other)

    def __le__(self, other):
        if not isinstance(other, MonitorMode):
            raise NotImplemented('Comparing MonitorNodes to non-MonitorNodes is not supported (yet)')

        # You might want to do this with total ordering
        return self.__eq__(other) or self.__lt__(other)

    def __eq__(self, other):
        if not isinstance(other, MonitorMode):
            raise NotImplemented('Comparing MonitorNodes to non-MonitorNodes is not supported (yet)')

        return self.height == other.height and self.width == other.width and self.refresh == other.refresh


class Monitor:
    def __init__(self, meta_data, connection):
        # TODO: Validate if screen valid @p :6
        self._set_modes(meta_data.pop('modes'), meta_data.pop('current_mode') if 'current_mode' in meta_data else None)
        self.name = meta_data['name']
        self.active = meta_data.pop('active')
        self.meta_data = meta_data
        self.connection = connection

    # Actions
    def enable(self, pos=None, mode=None, background=None):
        # TODO: Check if output exists and is disabled @p :1

        actions = []

        if pos is None:
            self.perform(["enable"])
            return

        if mode is None:
            mode = self.get_highest_mode()

        if pos:
            actions.append("position {:n} {:n}".format(pos[0], pos[1]))

        if mode:
            actions.append("resolution {:n}x{:n}".format(mode.width, mode.height))

        if background:
            actions.append("bg {:s} fill".format(background))
            
        self.perform(actions)

    def disable(self):
        self.perform(['disable'])

    def background(self, path, sizing=None):
        if not sizing:
            sizing = "fill"

        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError('Specified background does not exists')

        self.perform(["bg {:s} {:s}".format(path, sizing)])

    def mode(self, mode):
        if not isinstance(mode, MonitorMode):
            raise TypeError('Not a valid mode was provided')

        self.perform("resolution {:n}x{:n}".format(mode['height'], mode['width']))

    def refresh_modes(self, identifier=None):
        if identifier is None:
            identifier = 'name'

        data = self.connection.get_outputs()
        for monitor_data in data:
            if monitor_data[identifier] == self.meta_data[identifier]:
                self._set_modes(monitor_data.pop('modes'), monitor_data.pop('current_mode') if 'current_mode' in monitor_data else None)

    def perform(self, actions):
        command_parts = ["output {:s}".format(self.name)]
        command_parts.extend(actions)
        self.connection.command(" ".join(command_parts))

    # Checks
    def has_property(self, prop):
        return self.meta_data[prop[0]] == prop[1]

    def has_properties(self, props):
        logger.debug('Checking for properies {:s}'.format(json.dumps(props)))
        for prop in props.items():
            if not self.has_property(prop):
                return False

        return True

    def find_mode(self, expected_mode):
        for mode in self.meta_data['modes']:
            for expected_mode_attr, expected_value in expected_mode.items():
                if not mode[expected_mode_attr] == expected_value:
                    break

        return False

    def has_mode(self, expected_mode):
        raise NotImplemented('Has mode is not implented yet')

    def is_active(self):
        return self.active

    # Getters
    def get_attr(self):
        return self.meta_data

    def get_highest_mode(self):
        if not self.is_active():
            # TODO: We could enable the monitor to get the modes, but this walks into race condititions @p :0
            self.enable()
            self.refresh_modes()
            #raise Exception('Monitor is not active')

        if len(self.modes) == 0:
            raise Exception('Monitor has no modes')

        return max(self.modes)

    def get_active_mode(self):
        for mode in self.modes:
            if mode.active:
                return mode

    def get_mode(self, props):
        # TODO: Check if mode has the right refresh rate @p :10
        matching_modes = [mode for mode in self.modes if mode.has_dimensions(props)]

        if len(matching_modes) == 0:
            raise MonitorModeNotFoundError()

        # FIXME: This is not a valid way to do this @p :5
        if len(matching_modes) > 1:
            raise AmbigiousMonitorModeError()

        return matching_modes

    # Private
    def _set_modes(self, modes, active=None):
        self.modes = [MonitorMode(mode) for mode in modes]
        if active:
            self._set_active_mode(active)
    
    def _set_active_mode(self, active):
        active_mode = MonitorMode(active)
        for mode in self.modes:
            mode.active = mode == active_mode


class Setup:
    def __init__(self, fetch=True, connection=None):
        self.monitors = None
        if connection:
            self.connection = connection
        else:
            import i3ipc
            self.connection = i3ipc.Connection()
        if fetch:
            self.fetch_monitors()

    def fetch_monitors(self):
        monitors = []
        for monitor_data in self.connection.get_outputs():
            monitors.append(Monitor(monitor_data, self.connection))

        self.monitors = monitors

    def load_monitors(self, data):
        monitors = []
        for monitor in data:
            monitors.append(Monitor(monitor, self.connection))

        self.monitors = monitors
    
    def enable_left_to_right(self, monitors, align_top=True):
        for monitor in self.active_monitors():
            if monitor not in monitors:
                monitor.disable()


        logger.info('Enabling {:n} monitors'.format(len(monitors)))


        x_total = 0
        for monitor in monitors:
            logger.info('Enabling monitor {:s}'.format(monitor.name))
            mode = monitor.get_highest_mode()
            monitor.enable((x_total, 0), mode)
            x_total += mode.width

    def disable_all_monitors(self):
        # Bad idea, sway does not like it if you have no monitors enabled
        for monitor in self.active_monitors():
            monitor.disable()

    def active_monitors(self):
        monitors = self.monitors
        return filter(lambda monitor: monitor.active, monitors)

    def find_monitor(self, properties):
        monitor = list(filter(lambda monitor: monitor.has_properties(properties), self.monitors))

        if len(monitor) > 1:
            raise AmbigiousMonitorError('Monitor is ambigious')

        if len(monitor) == 0:
            raise MonitorNotFoundError('Could not find monitor')

        return monitor[0]

    def find_monitors(self, props_list):
        return list(map(self.find_monitor, props_list))

    def is_connected(self, screen_properties):
        # TODO: Think of a clearer name for this method @p :1
        try:
            self.find_monitor(screen_properties)
            return True
        except MonitorNotFoundError:
            # TODO: Custom monitor not found exception @p :2
            return False

    def check_setup(self, props_list):
        for props in props_list:
            if not self.is_connected(props):
                return False

        return True

    def check_and_enable_setup(self, props_list):
        if self.check_setup(props_list):
            logger.info('Found setup')
            self.enable_left_to_right(self.find_monitors(props_list))
            return True
        else:
            logger.info('Setup not found')

        return False


# Abstract to different module
class AmbigiousMonitorError(Exception):
    pass


class MonitorNotFoundError(Exception):
    pass


class AmbigiousMonitorModeError(Exception):
    pass


class MonitorModeNotFoundError(Exception):
    pass
