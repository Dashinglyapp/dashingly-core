define(['app', 'angular'], function (app, angular) {
	app.register.controller('RemovedCtrl', ['$scope', function ($scope) {
		$scope.hashkey = $scope.widgetData.hashkey;

		$scope.viewData = {
			"long": {
				"text": "This widget is currently unavailable.  Please contact your server administrator for more help."
			},
			"short": {
				"text": "Widget not available right now."
			}
		};
	}]);

});

