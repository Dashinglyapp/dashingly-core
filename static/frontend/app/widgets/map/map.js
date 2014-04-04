define(['app', 'angular', 'moment', 'view', 'context', 'user', 'realize-sync'], function (app, angular, moment) {
	app.register.controller('MapCtrl', ['$scope', 'sync', 'user', 'EVENTS', 'view', 'context', function ($scope, sync, user, EVENTS, view, context) {
		$scope.hashkey = $scope.widgetData.hashkey;
		$scope.formData = {};

		$scope.render = function () {
			view.getDetail(context.getScopeName(), context.getScopeHash(), $scope.widgetData.settings.source.value).then(function (data) {


				$scope.viewData = {
					map: {

					}
				};
			});
		};

		// change settings when an ancestor widget broadcasts to do it.
		$scope.$onRootScope(EVENTS.widgetSettingsChange, function (event, widgetKey) {
			console.log("Chart received settings change event", widgetKey);
			if (widgetKey === $scope.hashkey) {
				$scope.render();
			}
		});

		$scope.render();

	}]);
});

