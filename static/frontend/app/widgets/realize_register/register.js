define(['app', 'angular'], function (app, angular) {
	app.register.controller('RegisterCtrl', ['$scope', '$q', '$window', 'user', 'sync', function ($scope, $q, $window, user, sync) {
		console.log('RegisterCtrl scope', $scope);
		$scope.data = {};

		$scope.register = function () {
			user.loginOrRegister($scope.data, "register").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};
	}]);
});

