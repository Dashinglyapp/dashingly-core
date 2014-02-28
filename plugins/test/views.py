from core.plugins.views import BaseView

class GetStuffView(BaseView):
    path = "hello"

    def get(self, data):
        return "Hello"