define(['app', 'angularAMD', 'angular', 'jquery', 'angular-ui-bootstrap', 'realize-sync', 'widget', 'user', 'screen'], function (app, angularAMD, angular, $) {
	app.register.controller('WidgetDashboardCtrl', ['$scope', 'widget', 'widgetMeta', '$element', '$rootScope', 'sync', 'user', 'EVENTS', 'screen', '$modal', function ($scope, widget, widgetMeta, $element, $root, sync, user, EVENTS, screen, $modal) {
		$scope.hashkey = $scope.widgetData.hashkey;
		$scope.itemMap = {
			sizeX: 'widgetData.layout.sizeX',
			sizeY: 'widgetData.layout.sizeY',
			row: 'widgetData.layout.row',
			col: 'widgetData.layout.col'
    	};

		$scope.gridsterOpts = {
		  columns: 4, // the width of the grid, in columns
		  colWidth: 'auto', // can be an integer or 'auto'.  'auto' uses the pixel width of the element divided by 'columns'
		  rowHeight: 125, // can be an integer or 'match'.  Match uses the colWidth, giving you square widgets.
		  margins: [10, 10], // the pixel distance between each widget
		  defaultSizeX: 4, // the default width of a gridster item, if not specifed
      	  defaultSizeY: 2, // the default height of a gridster item, if not specifie
		  mobileBreakPoint: 600, // if the screen is not wider that this, remove the grid layout and stack the items
		  resize: {
			 enabled: false
		  },
		  draggable: {
			 enabled: true,
			 stop: function(event, uiWidget, $element) {
				 $scope.updateWidgetPositions();
			 }
		  }
		};

		console.log("Loaded dashboard widget", $scope.hashkey);
		$scope.type = "widgets";
		var modalInstance;

		$scope.updateWidgetPositions = function(){
			var hashkeys = [];
			for(var i = 0; i < $scope.loadedWidgets.length; i++){
				hashkeys.push({
					hashkey: $scope.loadedWidgets[i].hashkey,
					layout: $scope.loadedWidgets[i].layout
				});
			}
			widget.updateWidgetPositions(hashkeys);
		};

		$scope.open = function () {

			modalInstance = $modal.open({
				templateUrl: 'widgetModal.tpl.html',
				scope: $scope
			});
		};

		$scope.ok = function () {
			$modal.$close();
		};

		$scope.setupDashboard = function () {
			$scope.data = widget.listInstalledByParent($scope.hashkey).then(function (data) {
				$scope.loadedWidgets = data;
			});
		};

		$scope.add = function (widgetObj) {
			var timestamp = new Date().getTime();
			widgetObj.name = widgetObj.name + "_" + timestamp;
			widgetObj.parent = $scope.hashkey;

			console.log("Adding a widget to the dashboard: ", widgetObj);
			widget.create(widgetObj).then(function (data) {
				$scope.loadedWidgets.push(data);
			});
		};

		$scope.$onRootScope(EVENTS.widgetSettingsChange, function (event, widgetKey) {
			console.log("Dashboard received settings change event", widgetKey);
			if (widgetKey === $scope.hashkey) {
				$scope.setupDashboard();
			}
		});

		$scope.$onRootScope(EVENTS.widgetAddToDash, function (event, hashkey, widgetObj) {
			console.log("Dashboard received widget add event", hashkey);
			if (hashkey === $scope.hashkey) {
				$scope.add(widgetObj);
			}
		});

		$scope.$watch('loadedWidgets', function(newVal, oldVal){
			if(newVal !== undefined){
				$scope.gridsterOpts.minRows = newVal.length;
				$scope.gridsterOpts.maxRows = newVal.length;
			}
		});

		$scope.setupDashboard();
	}]);
});

