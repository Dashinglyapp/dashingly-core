define(['app', 'angular', 'user'], function (app, angular) {
	app.register.controller('IndexCtrl', ['$scope', 'user', 'EVENTS', function ($scope, user, EVENTS) {

		$scope.data = {};
		$scope.switch = function (type) {
			console.log('switchToLogin.clicked!');
			$scope.$emit(EVENTS.switchWidgetTree, type, 'default');
		};

		$scope.register = function () {
			user.loginOrRegister($scope.data, "register").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};

	}]);
});