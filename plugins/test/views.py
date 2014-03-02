from core.plugins.lib.views import BaseView

class GetStuffView(BaseView):
    path = "hello"

    def get(self, data):
        return "Hello"