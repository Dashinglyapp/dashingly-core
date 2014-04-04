define(['app', 'angular', 'user', 'realize-sync'], function (app, angular) {
	app.register.controller('LoginCtrl', ['$scope', '$q', '$window', 'user', 'sync', function ($scope, $q, $window, user, sync) {
		console.log('LoginCtrl scope', $scope);
		$scope.data = {};

		$scope.login = function () {
			user.loginOrRegister($scope.data, "login").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};
	}]);
});

