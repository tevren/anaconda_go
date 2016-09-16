
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from functools import partial

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.helpers import get_settings
from anaconda_go.lib.plugin import Worker, Callback, JediUsages, is_code

import sublime
import sublime_plugin


class AnacondaGoEncFunc(sublime_plugin.WindowCommand):
    """Get the enclosing function defined in the file and go to its header
    """

    def run(self) -> None:
        try:
            view = self.window.active_view()
            row, col = view.rowcol(view.sel()[0].begin())
            offset = view.text_point(row, col)
            data = {
                'vid': view.id(),
                'file_path': view.file_name(),
                'offset': offset,
                'parse_comments': get_settings(
                    view, 'anaconda_go_motion_parse_comments', False
                ),
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'enclosing',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=partial(JediUsages(self).process, False),
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except Exception as err:
            print('anaconda_go: enclosing function error')
            print(err)

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go')

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: enclosing function error')
        print(data['error'])

    def _on_timeout(self, _):
        """Fired when the callback times out
        """

        print('Golang enclosing function timed out')