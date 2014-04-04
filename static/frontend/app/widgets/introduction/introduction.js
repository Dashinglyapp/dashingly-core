define(['app', 'angular'], function (app, angular) {
	app.register.controller('IntroCtrl', ['$scope', function ($scope) {
		$scope.hashkey = $scope.widgetData.hashkey;

		$scope.viewData = {
			"long": {
				"text": "Welcome to your new dashboard!  Widgets are visual elements that can show you charts, text, maps, and anything else you could want (you can even make your own!).  Get started by clicking on 'add widget' above."
			},
			"short": {
				"text": "Welcome to your dashboard!  Click on 'add widgets' above to add a widget."
			}
		};
	}]);

});

